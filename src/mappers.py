# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import ast
from collections.abc import Container

import expressions
import utils


def map_scope(scope, fn):
    """Applies the mapping function to every statement in the scope.

    The mapping function should return a list of statements; the returned
    statements will be flattened together."""
    kwargs = {field: value for field, value in ast.iter_fields(scope)}
    body = []
    for stmt in scope.body:
        body.extend(fn(stmt))
        # TODO(tylerhou): Should we map all scopes?
        if utils.is_supported_scope(stmt):
            body[-1] = map_scope(body[-1], fn)
    kwargs["body"] = body
    return type(scope)(**kwargs)


def promote_to_temporary_m(fns: Container[str], name_iter):
    """Creates a function mapper that promotes the results of inner calls to
    functions in fns to temporary variables."""
    def promote_mapper(stmt):
        stmts = []
        stmts.append(expressions.promote_call_expressions(
            stmt, fns, name_iter, stmts))  # Mutates stmts
        return stmts
    return promote_mapper


def remove_trivial_temporaries_m(fn_ast: ast.AST):
    """Creates a function mapper that removes trivial assignments."""
    trivial_temps = set(utils.potentially_trivial_temporaries(fn_ast))
    first_assignment, last_assignment = utils.find_assignments(fn_ast, trivial_temps)
    trivial_temps = set(t for t in trivial_temps if last_assignment[t] is first_assignment[t])
    trivial_assignments = set(last_assignment[t] for t in trivial_temps)
    to_replace = {temp: last_assignment[temp] for temp in trivial_temps if temp in trivial_temps}


    def remove_trivial_mapper(stmt):
        return [] if stmt in trivial_assignments else [utils.replace_variable(stmt, to_replace)]
    return remove_trivial_mapper


def for_to_while_m(name_iter):
    """Creates a function mapper that converts for loops to equivalent while loops."""
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
    """Creates a function mapper that promotes the test in while loops to a variable."""
    def mapper(stmt):
        if not isinstance(stmt, ast.While):
            return [stmt]
        if isinstance(stmt.test, ast.Name):
            return [stmt]
            # TODO(tylerhou): Add a test for this.
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
            stmt, name_iter, stmts))  # Mutates stmts
        return stmts
    return mapper


def lift_to_frame_m(name_fn=lambda x: x):
    """Creates a function mapper that replaces all accesses where name_fn
    returns not None to loads and stores in a frame object."""
    def mapper(stmt):
        return [expressions.promote_variable_access(stmt, name_fn)]
    return mapper
