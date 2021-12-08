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


def fn_call_names(stmt: ast.AST, fns: Container[str]):
    for node in ast.walk(stmt):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in fns:
                yield node.func.id


def make_prev_dict(block: ast.AST):
    prev_dict = {}

    def helper(block: ast.AST):
        assert utils.is_block(block)
        for i, stmt in enumerate(block.body):
            if 0 <= i - 1:
                assert stmt not in prev_dict
                prev_dict[stmt] = block.body[i - 1]
        for stmt in block.body:
            if utils.is_block(stmt):
                helper(stmt)
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


def fiber_locals(fn_tree: ast.FunctionDef):
    local_vars = utils.local_vars(fn_tree)
    local_vars.add(jumps.PC_LOCAL_NAME)
    return local_vars


def insert_jumps(fn_tree: ast.FunctionDef, prev_dict, fns):
    prev_dict = make_prev_dict(fn_tree)
    body, _ = jumps.insert_jumps(
        fn_tree.body, jump_to=lambda stmt: needs_jump(stmt, prev_dict, fns))
    return body


def lift_locals_to_frame(fn_tree: ast.FunctionDef):
    local_vars = fiber_locals(fn_tree)
    return mappers.map_scope(fn_tree, mappers.lift_to_frame_m(
        name_fn=lambda x: x if x in local_vars else None))


def needs_jump(stmt: ast.AST, prev_dict, fns):
    if not stmt in prev_dict:
        return False

    # Check whether the child function is a trampoline.
    fn_calls = list(fn_call_names(prev_dict[stmt], fns))
    if not fn_calls:
        return False
    for name in fn_calls:
        if not (name in FIBER_FN_NAME_MAP or name in fns):
            return False

    return not is_tail_call(prev_dict[stmt])


def compile_tree(tree: ast.AST, fn, local_vars):
    tree = ast.fix_missing_locations(tree)
    code = compile(tree, f"<fiber> {inspect.getfile(fn)}", "exec")
    results = {}
    exec(code, dict([*fn.__globals__.items(), *
         OP_MAP.items(), *local_vars.items()]), results)
    results[tree.body[0].name].__fibercode__ = ast.unparse(tree)
    return results[tree.body[0].name]


# This is hacky...

@dataclass
class FiberMetadata:
    fn_def: ast.FunctionDef
    fn: Any


FIBER_FN_NAME_MAP = {}
FIBER_FN_COMPILED_MAP = {}


def add_trampoline_returns(block: ast.AST, fns: Container[str]):
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
            add_trampoline_returns(stmt, fns)
            continue
        if matches_callop(stmt, fns):
            replaced = make_callop_expr(stmt.targets[0].slice, stmt.value)
        elif matches_tailcallop(stmt, fns):
            replaced = make_tailcallop_expr(stmt.value)
        elif matches_retop(stmt, fns):
            replaced = make_retop_expr(stmt.value)
        else:
            continue
        assert index + 1 < len(body)
        assert is_pc_assign(body[index + 1])
        body[index], body[index + 1] = body[index+1], replaced


def fiber(fns: Container[str] = None, *, locals, recursive=True):
    """Returns a decorator that converts a function to a fiber.

    A fiber is a userspace scheduled thread. In this fiber implementation, we
    yield to the userspace scheduler whenever a listed function is called.

    Suppose we are executing a function A. When A reaches a call to some
    function B in fns, instead of calling the B directly, A will return a call
    operation to a trampoline. The trampoline will call the B with the correct
    arguments. After B finishes executing, the trampoline will resume A,
    passing B's return value.

    >>> @fiber(locals=locals())
    ... def fib(n):
    ...     if n <= 1: return n
    ...     return fib(n-1) + fib(n-2)
    ...
    >>> import trampoline
    >>> trampoline.run(fib, [10])
    55
    """

    if fns is None:
        fns = set()
    for fiber_fn in FIBER_FN_NAME_MAP:
        fns = set(fns)
        fns.add(fiber_fn)
    if callable(fns):
        raise ValueError("Did you forget to call the fiber decorator?")

    def make_fiber(fn):
        if recursive:
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
        fn_tree.body = insert_jumps(fn_tree, prev_dict, fns)
        fn_tree = lift_locals_to_frame(fn_tree)
        add_trampoline_returns(fn_tree, fns)
        fix_fn_def(fn_tree, fn)

        tree.body[0] = fn_tree
        fiber_fn = compile_tree(tree, fn, locals)

        lookup = FiberMetadata(get_tree(fn).body[0], fiber_fn)
        FIBER_FN_NAME_MAP[fn.__name__] = lookup
        FIBER_FN_COMPILED_MAP[fiber_fn] = lookup
        return fiber_fn

    return make_fiber
