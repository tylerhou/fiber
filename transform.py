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
        assignments.append(utils.make_assign(name, new_statement))
        return utils.make_lookup(name)
    return new_statement


def promote_to_temporary(fn_ast: ast.AST, fns: Container[str], name_iter):
    """Given the AST for a function, promotes the results of inner calls to
    functions in fns to temporary variables."""
    assert isinstance(fn_ast, ast.FunctionDef)

    def promote_mapper(stmt):
        statements = []
        statements.append(promote_call_expressions(
            stmt, fns, name_iter, statements))
        return statements
    fn_ast = utils.map_scope(fn_ast, promote_mapper)

    trivial_temps = utils.trivial_temporaries(fn_ast)
    assignments = utils.find_last_assignments(fn_ast, set(trivial_temps))
    assignments_values = set(assignments.values())

    def remove_trivial_mapper(stmt):
        return [] if stmt in assignments_values else [utils.replace_variable(stmt, assignments)]
    return utils.map_scope(fn_ast, remove_trivial_mapper)


def rewrite_for(fn_ast: ast.AST, name_iter):
    """Converts for loops to while loops."""
    def mapper(stmt):
        if isinstance(stmt, ast.For):
            iter_n, test_n = next(name_iter), next(name_iter)
            body = [utils.make_for_try(
                stmt.target, iter_n, test_n)] + stmt.body
            return [
                utils.make_assign(iter_n, utils.make_call("iter", stmt.iter)),
                utils.make_assign(test_n, ast.Constant(value=True)),
                ast.While(test=utils.make_lookup(test_n),
                          body=body, orelse=stmt.orelse),
            ]
        return [stmt]
    return utils.map_scope(fn_ast, mapper)

def rewrite_while():
    pass

def rewrite_boolops(fn_ast: ast.AST):
    """Rewrites boolean expressions as if statements so promotion to
    temporaries doesn't change evaluation semantics."""
