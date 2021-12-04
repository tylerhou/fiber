import ast
from collections.abc import Container
import utils


def promote_call_expressions(expression: ast.AST, fns: Container[str], name_iter, assignments):
    """Given a expression, transforms call expressions to functions in fns by
    promoting them to temporary variables. Appends promoting assignment
    expressions to assignments. Returns the new expression with call expressions
    replaced."""
    def map_attributes(expression, field, value):
        return promote_call_expressions(value, fns, name_iter, assignments)

    # Recursively map the expression's attributes (e.g. subexpressions).
    new_expression = utils.map_expression(expression, map_attributes)

    # If the function is a special function, then lift the expression to a
    # temporary. Also, replace the current expression with a reference to that
    # temporary.
    if isinstance(expression, ast.Call) and isinstance(expression.func, ast.Name) and expression.func.id in fns:
        name = next(name_iter)
        assignments.append(utils.make_assign(name, new_expression))
        return utils.make_lookup(name)
    return new_expression
