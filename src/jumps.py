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
from typing import List, Callable, Iterable
import utils

PC_LOCAL_NAME = "__pc"


def is_supported_jump_block(b: ast.AST):
    return any(isinstance(b, t) for t in (ast.While, ast.If))


def block_has_jump_to(block, jump_to: Callable[[ast.AST], bool]):
    return any(has_jump_to(stmt, jump_to) for stmt in block.body)


def has_jump_to(stmt: ast.AST, jump_to: Callable[[ast.AST], bool]):
    return jump_to(stmt) or (is_supported_jump_block(stmt) and block_has_jump_to(stmt, jump_to))


def partition_stmts(stmts: Iterable[ast.AST], jump_to: Callable[[ast.AST], bool]):
    """Splits statements into partitions with jump_to statements as dividers.
    The first statement in each partition is one that needs to be jumped to."""
    current = []
    for stmt in stmts:
        if has_jump_to(stmt, jump_to):
            yield current
            current = []
        current.append(stmt)
    yield current


def transform_if(stmt: ast.If, jump_to: Callable[[ast.AST], bool], next_pc):
    body, next_pc = insert_jumps(
        stmt.body, jump_to, next_pc)
    return ast.If(test=stmt.test, body=body, orelse=stmt.orelse), next_pc


def transform_while(stmt: ast.While, jump_to: Callable[[ast.AST], bool], next_pc):
    first_pc = next_pc
    body, next_pc = insert_jumps(stmt.body, jump_to, next_pc)
    # While loops jump back to the start of the loop.
    body.append(utils.make_assign(PC_LOCAL_NAME, ast.Constant(first_pc)))
    return ast.While(test=stmt.test, body=body, orelse=stmt.orelse), next_pc


def make_range_test(start_pc, end_pc):
    """Creates an boolean expression AST that checks whether the pc variable is
    in range(start, end)."""
    if start_pc + 1 == end_pc:
        return ast.Compare(
            left=utils.make_lookup(PC_LOCAL_NAME),
            ops=[ast.Eq()],
            comparators=[ast.Constant(value=start_pc)]
        )
    return ast.Compare(
        left=ast.Constant(value=start_pc),
        ops=[ast.LtE(), ast.Lt()],
        comparators=[utils.make_lookup(
            PC_LOCAL_NAME), ast.Constant(value=end_pc)],
    )


def transform_partition(partition, jump_to, next_pc):
    """Recursively transforms the partition, and wraps it in the appropriate if
    statement. Returns the new AST as well as the next pc value."""
    body = []
    start_pc = next_pc
    next_pc += 1  # Need at least one PC for this partition.
    for stmt in partition:
        transformed = stmt
        if isinstance(stmt, ast.If):
            # For blocks, the first inner PC is the same PC as the outer PC.
            transformed, next_pc = transform_if(stmt, jump_to, next_pc-1)
        elif isinstance(stmt, ast.While):
            transformed, next_pc = transform_while(stmt, jump_to, next_pc-1)
        body.append(transformed)
    end_pc = next_pc
    body.append(utils.make_assign(PC_LOCAL_NAME, ast.Constant(end_pc)))

    return ast.If(test=make_range_test(start_pc, end_pc), body=body, orelse=[]), next_pc


def insert_jumps(stmts: Iterable[ast.AST], jump_to: Callable[[ast.AST], bool], start_pc=0):
    """Inserts ifs into a sequence of statements such that each statement for
    which jump_to returns True has a pc value where entering the sequence with
    that value jumps to that statement.

    Only recursively inserts jumps inside child if and for blocks. If your
    block has for loops, then use for_to_while_m to rewrite them to while.

    Returns a new list of statements and the total number of jumps inserted.
    """
    new_stmts = []
    next_pc = start_pc
    for partition in partition_stmts(stmts, jump_to):
        if not partition:
            continue
        transformed, next_pc = transform_partition(partition, jump_to, next_pc)
        new_stmts.append(transformed)
    return new_stmts, next_pc
