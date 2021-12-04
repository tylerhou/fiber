import ast
from collections.abc import Container
import utils
from itertools import count
import expressions


def promote_to_temporary_m(fns: Container[str], name_iter):
    """Creates a function mapper that promotes the results of inner calls to
    functions in fns to temporary variables."""
    def promote_mapper(stmt):
        stmts = []
        stmts.append(expressions.promote_call_expressions(
            stmt, fns, name_iter, stmts))  # mutates stmts
        return stmts
    return promote_mapper


def remove_trivial_m(fn_ast: ast.AST):
    """Creates a function mapper that removes trivial assignments."""
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


def bool_exps_to_if_m(name_iter):
    """Creates a function mapper that rewrites boolean expressions as if
    statements so promotion to temporaries doesn't change evaluation order."""
    def mapper(stmt):
        stmts = []
        stmts.append(expressions.promote_boolean_expression_operands(
            stmt, name_iter, stmts))  # mutates stmts
        return stmts
    return mapper


def lift_to_frame_m(name_fn=lambda x: x):
    """Creates a function mapper that replaces all accesses where name_fn
    returns not None to loads and stores in a frame object."""
    def mapper(stmt):
        return [expressions.promote_variable_access(stmt, name_fn)]
    return mapper
