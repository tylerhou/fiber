import ast
from collections.abc import Container
import utils
import itertools


def promote_call_expressions(expression: ast.AST, fns: Container[str], name_iter, assignments):
    """Given a expression, transforms call expressions to functions in fns by
    promoting them to temporary variables. Appends promoting assignment
    expressions to assignments. Returns the new expression with call expressions
    replaced."""
    def map_attributes(field, expression):
        return promote_call_expressions(expression, fns, name_iter, assignments)

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


def make_and_if(name: str, expression: ast.AST, body):
    return ast.If(
        test=utils.make_lookup(name),
        body=body,
        orelse=[],
    )


def make_or_if(name: str, expression: ast.AST, body):
    return ast.If(
        test=utils.make_not(utils.make_lookup(name)),
        body=body,
        orelse=[],
    )


def promote_boolean_expression_operands(expression: ast.AST, name_iter, lines):
    """Given a expression, transforms boolean expressions by promoting their
    operands to temporary values assigned to by if expressions.  Returns the
    resulting temporary variable, and appends to lines the corresponding if
    expressions that populate the variable.
    """
    def map_attributes(field, expression):
        # If the expression is a boolop, append if statements to lines.
        if isinstance(expression, ast.BoolOp):
            assert len(expression.values) > 0
            maker = make_or_if if isinstance(
                expression.op, ast.Or) else make_and_if
            name = next(name_iter)
            lines.append(utils.make_assign(name, expression.values[0]))
            for child in itertools.islice(expression.values, 1, None):
                body = []
                body.append(promote_boolean_expression_operands(
                    utils.make_assign(name, child),
                    name_iter,
                    body,
                ))
                lines.append(maker(name, child, body))
            return utils.make_lookup(name)
        return promote_boolean_expression_operands(expression, name_iter, lines)

    # Recursively map the expression's attributes (e.g. subexpressions).
    return utils.map_expression(expression, map_attributes)


FRAME_LOCAL_NAME = "frame"


def promote_variable_access(expression: ast.AST, name_fn):
    def map_attributes(field, expression):
        if isinstance(expression, ast.Name) and (name := name_fn(expression.id)) is not None:
            return ast.Subscript(
                ctx=expression.ctx,
                slice=ast.Constant(value=name),
                value=ast.Name(id=FRAME_LOCAL_NAME, ctx=ast.Load())
            )
        return promote_variable_access(expression, name_fn)
    return utils.map_expression(expression, map_attributes)
