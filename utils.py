import ast
import itertools
from typing import Set, List

# We don't support exceptions (ast.Try) or async for/while.
# Exception support is fairly easy to add; async is harder.
FN_INNER_SCOPE_NODES = [ast.For, ast.While, ast.If, ast.While]


def dunder_names(prefix):
    for i in itertools.count():
        yield f"__${prefix}{i}__"


def is_scope(tree):
    return any(isinstance(tree, scope_type) for scope_type in FN_INNER_SCOPE_NODES)


def map_ast(tree: ast.AST, fn):
    kwargs = {}
    for field, value in ast.iter_fields(tree):
        kwargs[field] = fn(tree, field, value)
    return type(tree)(**kwargs)


def fmap_statements(scope, fn):
    """Applies the mapping function to every statement in the scope.

    The mapping function should return a list of statements; the returned
    statements will be flattened together."""
    kwargs = {field: value for field, value in ast.iter_fields(scope)}
    body = []
    for stmt in scope.body:
        body.extend(fn(stmt))
        if is_scope(stmt):
            body[-1] = fmap_statements(body[-1], fn)
    kwargs["body"] = body
    return type(scope)(**kwargs)
