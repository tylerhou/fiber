import ast
from collections.abc import Container
from utils import dunder_names, is_scope, map_ast, fmap_statements


def promote_call_expressions(tree: ast.AST, fns: Container[str], names, assignments):
    """Given an AST, transforms call expressions to functions in fns by
    promoting them to temporary variables. Appends promoting assingment
    statements to assignments. Returns the new expression with call expressions
    replaced."""
    def mapper(tree, field, value):
        if is_scope(tree) and field == "body":
            # Do not traverse the body of scopes; only promote recursive calls
            # inside the scope header.
            return value
        if isinstance(value, list):
            return [
                promote_call_expressions(child, fns, names, assignments)
                for child in value
                if isinstance(child, ast.AST)
            ]
        elif isinstance(value, ast.AST):
            return promote_call_expressions(value, fns, names, assignments)
        return value

    new_tree = map_ast(tree, mapper)
    if isinstance(tree, ast.Call) and isinstance(tree.func, ast.Name) and tree.func.id in fns:
        name = next(names)
        assignments.append(ast.Assign(
            targets=[ast.Name(id=name, ctx=ast.Store())], value=new_tree))
        return ast.Name(id=name, ctx=ast.Load())
    return new_tree


def promote_to_temporary(tree: ast.AST, fns: Container[str], names=lambda: dunder_names("tmp")):
    """Given the AST for a function, promotes the results of inner calls to
    functions in fns to temporary variables."""
    from collections import defaultdict
    assert isinstance(tree, ast.FunctionDef)

    # assignment_nodes[scope][line] contains assignment nodes that should be
    # inserted before that line.
    assignment_nodes = defaultdict(lambda: defaultdict(list))
    names_iter = names()

    def mapper(stmt):
        assignments = []
        result = promote_call_expressions(stmt, fns, names_iter, assignments)
        assignments.append(result)
        return assignments

    tree = fmap_statements(tree, mapper)
    return tree
