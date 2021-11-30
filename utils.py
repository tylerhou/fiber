import ast
import itertools
import re

# We don't support exceptions (ast.Try) or async for/while.
# Exception support is fairly easy to add; async is harder.
FN_INNER_SCOPE_NODES = [ast.For, ast.While, ast.If, ast.While]


def dunder_names():
    for i in itertools.count():
        yield f"__$tmp{i}__"


dunder_regex = re.compile(r'__\$tmp\d+__')


def is_temporary(name):
    return re.match(dunder_regex, name) != None


def is_scope(tree):
    return any(isinstance(tree, scope_type) for scope_type in FN_INNER_SCOPE_NODES)


def map_statement(statement: ast.AST, fn):
    """Transforms a statement's fields by the mapping function."""
    kwargs = {}
    for field, value in ast.iter_fields(statement):
        kwargs[field] = fn(statement, field, value)
    return type(statement)(**kwargs)


def map_scope(scope, fn):
    """Applies the mapping function to every statement in the scope.

    The mapping function should return a list of statements; the returned
    statements will be flattened together."""
    kwargs = {field: value for field, value in ast.iter_fields(scope)}
    body = []
    for stmt in scope.body:
        body.extend(fn(stmt))
        if is_scope(stmt):
            body[-1] = map_scope(body[-1], fn)
    kwargs["body"] = body
    return type(scope)(**kwargs)


def iter_scope(scope):
    """Iterates through every statement in the scope, recursively."""
    for stmt in scope.body:
        yield stmt
        if is_scope(stmt):
            yield from iter_scope(stmt)


def trivial_temporaries(fn):
    """Yields trivial temporaries (e.g. `return __$tmpX__`)"""
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
    def mapper(stmt, field, value):
        if field == "value":
            return assignments[stmt.value.id].value
        return value

    if isinstance(statement, ast.Return) and \
            isinstance(statement.value, ast.Name) and \
            statement.value.id in assignments:
        return map_statement(statement, mapper)

    if (isinstance(statement, ast.Assign) or
        isinstance(statement, ast.AnnAssign)) and \
        isinstance(statement.value, ast.Name) and \
            statement.value.id in assignments:
        return map_statement(statement, mapper)
    return statement


def make_assign(target, value):
    return ast.Assign(targets=[ast.Name(id=target, ctx=ast.Store())], value=value)


def make_call(func: str, *args):
    return ast.Call(func=ast.Name(id=func, ctx=ast.Load()), args=args, keywords=[])


def make_lookup(name: str):
    return ast.Name(id=name, ctx=ast.Load())


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
