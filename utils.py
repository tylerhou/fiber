import ast
import itertools
import re

# We don't support exceptions (ast.Try) or async for/while.
# Exception support is fairly easy to add; async is harder.
FN_INNER_SCOPE_NODES = [ast.For, ast.While, ast.If, ast.While]


def dunder_names():
    for i in itertools.count():
        yield f"__tmp{i}__"


dunder_regex = re.compile(r'__tmp\d+__')


def is_temporary(name):
    return re.match(dunder_regex, name) != None


def is_supported_scope(tree):
    return any(isinstance(tree, scope_type) for scope_type in FN_INNER_SCOPE_NODES)


def map_expression(statement: ast.AST, fn):
    """Recursively transforms an expression by applying the mapping function to
    all attributes that are AST nodes.

    Does not recursively transform scope bodies (while, for, try) as one would
    usually call this function from a mapper in map_scope, which itself already
    iterates through scope bodies."""
    kwargs = {}
    for field, value in ast.iter_fields(statement):
        result = value
        if is_supported_scope(statement) and field == "body":
            result = value
        elif isinstance(value, list):
            result = [fn(field, v)
                      for v in value if isinstance(v, ast.AST)]
        elif isinstance(value, ast.AST):
            result = fn(field, value)
        kwargs[field] = result
    return type(statement)(**kwargs)


def iter_scope(scope):
    """Iterates through every statement in the scope, recursively."""
    for stmt in scope.body:
        yield stmt
        if is_supported_scope(stmt):
            yield from iter_scope(stmt)


def trivial_temporaries(fn):
    """Yields trivial temporaries.

    Temporaries are trivial if they are directly assigned to another variable
    or if they are returned; e.g.
        t = __tmp1__
        return __tmp2__
    """
    for statement in iter_scope(fn):
        if isinstance(statement, ast.Return) and \
                isinstance(statement.value, ast.Name) and \
                is_temporary(statement.value.id):
            yield statement.value.id

        if (isinstance(statement, ast.Assign) or
                isinstance(statement, ast.AnnAssign)) and \
                isinstance(statement.value, ast.Name) and \
                is_temporary(statement.value.id):
            yield statement.value.id


def find_last_assignments(fn, variables):
    """Finds the last assignment for each variable."""
    mapping = {}
    for statement in iter_scope(fn):
        if isinstance(statement, ast.Assign) and \
                len(statement.targets) == 1 and \
                isinstance(statement.targets[0], ast.Name) and \
                (var := statement.targets[0].id) in variables:
            mapping[var] = statement
    return mapping


def replace_variable(statement, assignments):
    def mapper(field, expression):
        if field == "value":
            return assignments[expression.id].value
        return expression

    if isinstance(statement, ast.Return) and \
            isinstance(statement.value, ast.Name) and \
            statement.value.id in assignments:
        return map_expression(statement, mapper)

    if (isinstance(statement, ast.Assign) or
        isinstance(statement, ast.AnnAssign)) and \
        isinstance(statement.value, ast.Name) and \
            statement.value.id in assignments:
        return map_expression(statement, mapper)
    return statement


def make_assign(target, value):
    return ast.Assign(targets=[ast.Name(id=target, ctx=ast.Store())], value=value)


def make_call(func: str, *args):
    return ast.Call(func=ast.Name(id=func, ctx=ast.Load()), args=list(args), keywords=[])


def make_lookup(name: str):
    return ast.Name(id=name, ctx=ast.Load())


def make_not(exp: ast.AST):
    return ast.UnaryOp(op=ast.Not(), operand=exp)


def make_for_try(loop_target, iter_n, test_n):
    return ast.Try(
        body=[ast.Assign(targets=[loop_target], value=make_call(
            "next", make_lookup(iter_n)))],
        handlers=[
            ast.ExceptHandler(type=make_lookup("StopIteration"),
                              body=[
                                  make_assign(
                                      test_n, ast.Constant(value=False)),
                                  ast.Continue()
            ])],
        orelse=[],
        finalbody=[])


def is_block(block: ast.AST):
    return hasattr(block, "body") and isinstance(block.body, list)


def _locals_impl(fn: ast.AST):
    assert isinstance(fn, ast.FunctionDef)
    args = fn.args
    for arg in itertools.chain(args.posonlyargs, args.args, args.kwonlyargs, (args.vararg, args.kwarg)):
        if arg is not None:
            yield arg.arg

    def helper(block: ast.AST):
        for node in block.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        yield target.id
            if isinstance(node, ast.AnnAssign) or \
                    isinstance(node, ast.AugAssign) or \
                    isinstance(node, ast.NamedExpr):
                if isinstance(node.target, ast.Name):
                    yield node.target.id
            if is_block(node) and not isinstance(node, ast.FunctionDef):
                yield from helper(node)
    yield from helper(fn)


def local_vars(fn: ast.AST):
    """Returns a set of all function local variables."""
    return set(_locals_impl(fn))
