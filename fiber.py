import ast
from collections import ChainMap
from dataclasses import dataclass
import inspect
from typing import Any, Container, Dict, List, Set, Union
import textwrap

import jumps
import mappers
import utils


def get_tree(fn):
    lines = textwrap.dedent(inspect.getsource(fn)).split("\n")
    for i, line in enumerate(lines):
        if line.startswith("def"):
            break
    return ast.parse("\n".join(lines[i:]))


def has_fn_call_expression(stmt: ast.AST, fns: Container[str]):
    for node in ast.walk(stmt):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in fns:
                return True
    return False


def make_prev_dict(block: ast.AST):
    prev_dict = {}

    def helper(block: ast.AST):
        assert utils.is_block(block)
        for i, stmt in enumerate(block.body):
            if 0 <= i - 1:
                prev_dict[stmt] = block.body[i - 1]
        for stmt in block.body:
            if utils.is_block(stmt):
                make_prev_dict(stmt)
    helper(block)
    return prev_dict


@dataclass
class CallOp:
    func: Any
    args: List[Any]
    kwargs: Dict[Any, Any]
    ret_variable: str


@dataclass
class TailCallOp:
    func: Any
    args: List[Any]
    kwargs: Dict[Any, Any]


@dataclass
class RetOp:
    value: Any


OP_MAP = {
    CallOp.__name__: CallOp,
    TailCallOp.__name__: TailCallOp,
    RetOp.__name__: RetOp,
}


def matches_call(call: Union[ast.expr, None], fns: Container[str]):
    return isinstance(call, ast.Call) \
        and isinstance(call.func, ast.Name) \
        and call.func.id in fns


def matches_callop(stmt: ast.AST, fns: Container[str]):
    return isinstance(stmt, ast.Assign) and \
        len(stmt.targets) == 1 and \
        isinstance(target := stmt.targets[0], ast.Subscript) and \
        isinstance(target.value, ast.Name) and \
        target.value.id == "frame" and \
        matches_call(stmt.value, fns)


def matches_tailcallop(stmt: ast.AST, fns: Container[str]):
    return isinstance(stmt, ast.Return) and matches_call(stmt.value, fns)


def matches_retop(stmt: ast.AST, fns: Container[str]):
    return isinstance(stmt, ast.Return)


def is_pc_assign(stmt: ast.AST):
    return isinstance(stmt, ast.Assign) and \
        len(stmt.targets) == 1 and \
        isinstance(target := stmt.targets[0], ast.Subscript) and \
        isinstance(target.value, ast.Name) and \
        target.value.id == "frame" and \
        isinstance(name := target.slice, ast.Constant) and \
        name.value == jumps.PC_LOCAL_NAME and \
        isinstance(stmt.value, ast.Constant) and \
        isinstance(stmt.value.value, int)


def is_tail_call(stmt: ast.AST):
    return isinstance(stmt, ast.Return) and \
        isinstance(stmt.value, ast.Call)


def make_callop_expr(variable: ast.Constant, call: ast.Call):
    return ast.Return(
        value=ast.Call(
            func=utils.make_lookup(CallOp.__name__),
            args=[],
            keywords=[
                ast.keyword(arg="func", value=ast.Constant(
                    value=call.func.id)),
                ast.keyword(arg="args", value=ast.List(
                    elts=call.args, ctx=ast.Load())),
                ast.keyword(arg="kwargs", value=ast.Dict(
                    keys=[ast.Constant(k.arg) for k in call.keywords], values=[k.value for k in call.keywords])),
                ast.keyword(arg="ret_variable", value=variable),
            ]
        )
    )


def make_tailcallop_expr(call: ast.Call):
    return ast.Return(
        value=ast.Call(
            func=utils.make_lookup(TailCallOp.__name__),
            args=[],
            keywords=[
                ast.keyword(arg="func", value=ast.Constant(
                    value=call.func.id)),
                ast.keyword(arg="args", value=ast.List(
                    elts=call.args, ctx=ast.Load())),
                ast.keyword(arg="kwargs", value=ast.Dict(
                    keys=[ast.Constant(k.arg) for k in call.keywords], values=[k.value for k in call.keywords])),
            ]
        )
    )


def make_retop_expr(value: ast.AST):
    return ast.Return(
        value=ast.Call(
            func=utils.make_lookup(RetOp.__name__),
            args=[],
            keywords=[
                ast.keyword(arg="value", value=value)
            ]
        )
    )


def make_arguments():
    return ast.arguments(
        posonlyargs=[],
        args=[ast.arg(arg="frame")],
        kwonlyargs=[],
        kwarg=None,
        vararg=None,
        defaults=[],
        kw_defaults=[],
    )


def fix_fn_def(fn_tree: ast.FunctionDef, fn):
    fn_tree.name = f"__fiberfn_{fn.__name__}"
    fn_tree.args = make_arguments()


def compile_tree(tree: ast.AST, fn):
    tree = ast.fix_missing_locations(tree)
    code = compile(tree, f"<fiber> {inspect.getfile(fn)}", "exec")
    results = {}
    # TODO(tylerhou): Correctly get the function's nonlocals.
    # locls = ChainMap(results, *(inspect.stack(0)[1:]))
    exec(code, dict([*fn.__globals__.items(), *OP_MAP.items()]), results)
    results[tree.body[0].name].__fibercode__ = ast.unparse(tree)
    return results[tree.body[0].name]


# This is hacky...
FIBER_FUNCTIONS = {}


def replace_with_trampoline(block: ast.AST, fns: Container[str]):
    """Recursively mutates the block by replacing a function call or a return
    statement with a return to a trampoline. Also moves the PC assignment to
    before the return to the trampoline.

    We assume that all recursive calls have been lifted to temporaries, and
    tail calls are in `return call()` form (trivial temporary eliminated)."""
    assert utils.is_block(block)
    # Make a shallow copy, as we mutate the list as we iterate (by swapping).
    body = block.body
    for index, stmt in enumerate(list(body)):
        if utils.is_block(stmt):
            replace_with_trampoline(stmt, fns)
            continue
        if matches_callop(stmt, fns):
            replaced = make_callop_expr(stmt.targets[0].slice, stmt.value)
        elif matches_tailcallop(stmt, fns):
            replaced = make_tailcallop_expr(stmt.value)
        elif matches_retop(stmt, fns):
            replaced = make_retop_expr(stmt.value)
        else:
            continue
        assert index + 1 < len(body) and is_pc_assign(body[index + 1])
        body[index], body[index + 1] = body[index+1], replaced


def fiber(fns: Set[str] = None, *, recursive=True):
    """Returns a decorator that converts a function to a fiber.

    A fiber is a userspace scheduled thread. In this fiber implementation, we
    yield to the userspace scheduler whenever a listed function is called.

    Suppose we are executing a function A. When A reaches a call to some
    function B in fns, instead of calling the B directly, A will return a call
    operation to a trampoline. The trampoline will call the B with the correct
    arguments. After B finishes executing, the trampoline will resume A,
    passing B's return value."""

    # TODO(tylerhou): Add FIBER_FUNCTIONS to fns.
    def make_fiber(fn):
        nonlocal fns
        if recursive:
            fns = set(fns)
            fns.add(fn.__name__)

        tree = get_tree(fn)
        name_iter, fn_tree = utils.dunder_names(), tree.body[0]
        assert isinstance(fn_tree, ast.FunctionDef)

        transforms = [
            mappers.for_to_while_m(name_iter),
            mappers.promote_while_cond_m(name_iter),
            mappers.bool_exps_to_if_m(name_iter),
            mappers.promote_to_temporary_m(fns, name_iter),
        ]
        for t in transforms:
            fn_tree = mappers.map_scope(fn_tree, t)
        # These mappers need access to the new tree to preprocess variables.
        fn_tree = mappers.map_scope(fn_tree, mappers.remove_trivial_m(fn_tree))

        prev_dict = make_prev_dict(fn_tree)
        def needs_jump(stmt: ast.AST):
            return stmt in prev_dict and \
                has_fn_call_expression(prev_dict[stmt], fns) and \
                not is_tail_call(prev_dict[stmt])
        fn_tree.body, _ = jumps.insert_jumps(fn_tree.body, jump_to=needs_jump)

        locals = utils.locals(fn_tree)
        locals.add(jumps.PC_LOCAL_NAME)
        fn_tree = mappers.map_scope(fn_tree, mappers.lift_to_frame_m(
            lambda x: x if x in locals else None))

        replace_with_trampoline(fn_tree, fns)
        fix_fn_def(fn_tree, fn)

        tree.body[0] = fn_tree
        compiled = compile_tree(tree, fn)
        # TODO(tylerhou): Clean up
        FIBER_FUNCTIONS[fn.__name__] = (get_tree(fn).body[0], compiled)
        FIBER_FUNCTIONS[compiled] = (get_tree(fn).body[0], compiled)
        return compiled

    if fns is None:
        fns = set()
    if callable(fns):
        raise ValueError("Did you forget to call the fiber decorator?")
    return make_fiber
