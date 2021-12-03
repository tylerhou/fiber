import ast
from collections.abc import Container
import utils


def promote_call_expressions(statement: ast.AST, fns: Container[str], name_iter, assignments):
    """Given a statement, transforms call expressions to functions in fns by
    promoting them to temporary variables. Appends promoting assignment
    statements to assignments. Returns the new expression with call expressions
    replaced."""
    def map_attributes(statement, field, value):
        return promote_call_expressions(value, fns, name_iter, assignments)

    # Recursively map the statement's attributes (e.g. subexpressions).
    new_statement = utils.map_expression(statement, map_attributes)

    # If the function is a special function, then lift the expression to a
    # temporary. Also, replace the current expression with a reference to that
    # temporary.
    if isinstance(statement, ast.Call) and isinstance(statement.func, ast.Name) and statement.func.id in fns:
        name = next(name_iter)
        assignments.append(utils.make_assign(name, new_statement))
        return utils.make_lookup(name)
    return new_statement


def promote_to_temporary_m(fns: Container[str], name_iter):
    """Creates a function mapper that promotes the results of inner calls to
    functions in fns to temporary variables."""

    def promote_mapper(stmt):
        statements = []
        statements.append(promote_call_expressions(
            stmt, fns, name_iter, statements))
        return statements
    return promote_mapper

def remove_trivial_m(fn_ast: ast.AST):
    trivial_temps = utils.trivial_temporaries(fn_ast)
    assignments = utils.find_last_assignments(fn_ast, set(trivial_temps))
    assignments_values = set(assignments.values())

    def remove_trivial_mapper(stmt):
        return [] if stmt in assignments_values else [utils.replace_variable(stmt, assignments)]
    return remove_trivial_mapper


def for_to_while_m(name_iter):
    """Creates a function mapper that converts for loops to equivalent while
    loops."""
    def mapper(stmt):
        if not isinstance(stmt, ast.For):
            return [stmt]
        iter_n, test_n = next(name_iter), next(name_iter)
        body = [utils.make_for_try(stmt.target, iter_n, test_n)] + stmt.body
        return [
            utils.make_assign(iter_n, utils.make_call("iter", stmt.iter)),
            utils.make_assign(test_n, ast.Constant(value=True)),
            ast.While(test=utils.make_lookup(test_n),
                      body=body, orelse=stmt.orelse),
        ]
    return mapper


def promote_while_cond_m(name_iter):
    """Creates a function mapper that promotes the test in while loops to a
    variable."""
    def mapper(stmt):
        if not isinstance(stmt, ast.While):
            return [stmt]
        condition_n = next(name_iter)
        test_assign = utils.make_assign(condition_n, stmt.test)
        body = stmt.body + [test_assign]
        return [test_assign, ast.While(test=utils.make_lookup(condition_n), body=body, orelse=stmt.orelse)]
    return mapper

def rewrite_boolops(fn_ast: ast.AST):
    """Rewrites boolean expressions as if statements so promotion to
    temporaries doesn't change evaluation semantics."""
