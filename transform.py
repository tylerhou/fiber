import ast
from collections.abc import Container
import utils


def promote_call_expressions(statement: ast.AST, fns: Container[str], name_iter, assignments):
    """Given a statement, transforms call expressions to functions in fns by
    promoting them to temporary variables. Appends promoting assignment
    statements to assignments. Returns the new expression with call expressions
    replaced."""
    def mapper(statement, field, value):
        if utils.is_scope(statement) and field == "body":
            # Do not traverse the body of scopes; only promote recursive calls
            # inside the scope header.
            return value
        if isinstance(value, list):
            return [
                promote_call_expressions(child, fns, name_iter, assignments)
                for child in value
                if isinstance(child, ast.AST)
            ]
        elif isinstance(value, ast.AST):
            return promote_call_expressions(value, fns, name_iter, assignments)
        return value

    new_statement = utils.map_statement(statement, mapper)
    if isinstance(statement, ast.Call) and isinstance(statement.func, ast.Name) and statement.func.id in fns:
        name = next(name_iter)
        assignments.append(ast.Assign(
            targets=[ast.Name(id=name, ctx=ast.Store())], value=new_statement))
        return ast.Name(id=name, ctx=ast.Load())
    return new_statement


def promote_to_temporary(tree: ast.AST, fns: Container[str]):
    """Given the AST for a function, promotes the results of inner calls to
    functions in fns to temporary variables."""
    assert isinstance(tree, ast.FunctionDef)
    name_iter = utils.dunder_names()

    def promote_mapper(stmt):
        statements = []
        statements.append(promote_call_expressions(
            stmt, fns, name_iter, statements))
        return statements
    tree = utils.map_scope(tree, promote_mapper)

    trivial_temps = utils.trivial_temporaries(tree)
    assignments = utils.find_last_assignments(tree, set(trivial_temps))
    assignments_values = set(assignments.values())
    def remove_trivial_mapper(stmt):
        return [] if stmt in assignments_values else [utils.replace_variable(stmt, assignments)]
    return utils.map_scope(tree, remove_trivial_mapper)
