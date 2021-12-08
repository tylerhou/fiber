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

# Pass (0): Start

def matrix_chain_mult__helper(i, j):
    if i == j:
        return 0

    max_profit = float('-inf')
    for k in range(i, j):
        profit = matrix_chain_mult__helper(i, k)
        profit += matrix_chain_mult__helper(k + 1, j)
        profit += sizes[i - 1] * sizes[k] * sizes[j]
        max_profit = max(max_profit, profit)

    return max_profit


# ------------------------------------


# Pass (1): for_to_while

def matrix_chain_mult__helper(i, j):
    if i == j:
        return 0

    max_profit = float('-inf')
    __tmp0__ = iter(range(i, j))
    __tmp1__ = True
    while __tmp1__:
        try:
            k = next(__tmp0__)
        except StopIteration:
            __tmp1__ = False
            continue
        profit = matrix_chain_mult__helper(i, k)
        profit += matrix_chain_mult__helper(k + 1, j)
        profit += sizes[i - 1] * sizes[k] * sizes[j]
        max_profit = max(max_profit, profit)

    return max_profit


# ------------------------------------


# Pass (2): promote_while_cond

def matrix_chain_mult__helper(i, j):
    if i == j:
        return 0

    max_profit = float('-inf')
    __tmp0__ = iter(range(i, j))
    __tmp1__ = True
    while __tmp1__:
        try:
            k = next(__tmp0__)
        except StopIteration:
            __tmp1__ = False
            continue
        profit = matrix_chain_mult__helper(i, k)
        profit += matrix_chain_mult__helper(k + 1, j)
        profit += sizes[i - 1] * sizes[k] * sizes[j]
        max_profit = max(max_profit, profit)

    return max_profit


# ------------------------------------


# Pass (3): bool_exps_to_if

def matrix_chain_mult__helper(i, j):
    if i == j:
        return 0

    max_profit = float('-inf')
    __tmp0__ = iter(range(i, j))
    __tmp1__ = True
    while __tmp1__:
        try:
            k = next(__tmp0__)
        except StopIteration:
            __tmp1__ = False
            continue
        profit = matrix_chain_mult__helper(i, k)
        profit += matrix_chain_mult__helper(k + 1, j)
        profit += sizes[i - 1] * sizes[k] * sizes[j]
        max_profit = max(max_profit, profit)

    return max_profit


# ------------------------------------


# Pass (4): promote_to_temporary_m

def matrix_chain_mult__helper(i, j):
    if i == j:
        return 0

    max_profit = float('-inf')
    __tmp0__ = iter(range(i, j))
    __tmp1__ = True
    while __tmp1__:
        try:
            k = next(__tmp0__)
        except StopIteration:
            __tmp1__ = False
            continue
        __tmp2__ = matrix_chain_mult__helper(i, k)
        profit = __tmp2__
        __tmp3__ = matrix_chain_mult__helper(k + 1, j)
        profit += __tmp3__
        profit += sizes[i - 1] * sizes[k] * sizes[j]
        max_profit = max(max_profit, profit)

    return max_profit


# ------------------------------------


# Pass (5): remove_trivial_temporaries

def matrix_chain_mult__helper(i, j):
    if i == j:
        return 0

    max_profit = float('-inf')
    __tmp0__ = iter(range(i, j))
    __tmp1__ = True
    while __tmp1__:
        try:
            k = next(__tmp0__)
        except StopIteration:
            __tmp1__ = False
            continue
        profit = matrix_chain_mult__helper(i, k)
        __tmp3__ = matrix_chain_mult__helper(k + 1, j)
        profit += __tmp3__
        profit += sizes[i - 1] * sizes[k] * sizes[j]
        max_profit = max(max_profit, profit)

    return max_profit


# ------------------------------------


# Pass (6): insert_jumps

def matrix_chain_mult__helper(i, j):
    if __pc == 0:
        if i == j:
            if __pc == 0:
                return 0
                __pc = 1

        max_profit = float('-inf')
        __tmp0__ = iter(range(i, j))
        __tmp1__ = True
        __pc = 1
    if 1 <= __pc < 4:
        while __tmp1__:
            if __pc == 1:
                try:
                    k = next(__tmp0__)
                except StopIteration:
                    __tmp1__ = False
                    continue
                profit = matrix_chain_mult__helper(i, k)
                __pc = 2
            if __pc == 2:
                __tmp3__ = matrix_chain_mult__helper(k + 1, j)
                __pc = 3
            if __pc == 3:
                profit += __tmp3__
                profit += sizes[i - 1] * sizes[k] * sizes[j]
                max_profit = max(max_profit, profit)
                __pc = 4
            __pc = 1
        __pc = 4

    if __pc == 4:
        return max_profit
        __pc = 5


# ------------------------------------


# Pass (7): lift_locals_to_frame

def matrix_chain_mult__helper(i, j):
    if frame['__pc'] == 0:
        if frame['i'] == frame['j']:
            if frame['__pc'] == 0:
                return 0
                frame['__pc'] = 1

        frame['max_profit'] = float('-inf')
        frame['__tmp0__'] = iter(range(frame['i'], frame['j']))
        frame['__tmp1__'] = True
        frame['__pc'] = 1
    if 1 <= frame['__pc'] < 4:
        while frame['__tmp1__']:
            if frame['__pc'] == 1:
                try:
                    frame['k'] = next(frame['__tmp0__'])
                except StopIteration:
                    frame['__tmp1__'] = False
                    continue
                frame['profit'] = matrix_chain_mult__helper(frame['i'], frame['k'])
                frame['__pc'] = 2
            if frame['__pc'] == 2:
                frame['__tmp3__'] = matrix_chain_mult__helper(frame['k'] + 1, frame['j'])
                frame['__pc'] = 3
            if frame['__pc'] == 3:
                frame['profit'] += frame['__tmp3__']
                frame['profit'] += sizes[frame['i'] - 1] * sizes[frame['k']] * sizes[frame['j']]
                frame['max_profit'] = max(frame['max_profit'], frame['profit'])
                frame['__pc'] = 4
            frame['__pc'] = 1
        frame['__pc'] = 4

    if frame['__pc'] == 4:
        return frame['max_profit']
        frame['__pc'] = 5


# ------------------------------------


# Pass (8): add_trampoline_returns

def matrix_chain_mult__helper(i, j):
    if frame['__pc'] == 0:
        if frame['i'] == frame['j']:
            if frame['__pc'] == 0:
                frame['__pc'] = 1
                return RetOp(value=0)

        frame['max_profit'] = float('-inf')
        frame['__tmp0__'] = iter(range(frame['i'], frame['j']))
        frame['__tmp1__'] = True
        frame['__pc'] = 1
    if 1 <= frame['__pc'] < 4:
        while frame['__tmp1__']:
            if frame['__pc'] == 1:
                try:
                    frame['k'] = next(frame['__tmp0__'])
                except StopIteration:
                    frame['__tmp1__'] = False
                    continue
                frame['__pc'] = 2
                return CallOp(func='matrix_chain_mult__helper', args=[frame['i'], frame['k']], kwargs={}, ret_variable='profit')
            if frame['__pc'] == 2:
                frame['__pc'] = 3
                return CallOp(func='matrix_chain_mult__helper', args=[frame['k'] + 1, frame['j']], kwargs={}, ret_variable='__tmp3__')
            if frame['__pc'] == 3:
                frame['profit'] += frame['__tmp3__']
                frame['profit'] += sizes[frame['i'] - 1] * sizes[frame['k']] * sizes[frame['j']]
                frame['max_profit'] = max(frame['max_profit'], frame['profit'])
                frame['__pc'] = 4
            frame['__pc'] = 1
        frame['__pc'] = 4

    if frame['__pc'] == 4:
        frame['__pc'] = 5
        return RetOp(value=frame['max_profit'])


# ------------------------------------


# Pass (9): fix_fn_def

def __fiberfn_matrix_chain_mult__helper(frame):
    if frame['__pc'] == 0:
        if frame['i'] == frame['j']:
            if frame['__pc'] == 0:
                frame['__pc'] = 1
                return RetOp(value=0)

        frame['max_profit'] = float('-inf')
        frame['__tmp0__'] = iter(range(frame['i'], frame['j']))
        frame['__tmp1__'] = True
        frame['__pc'] = 1
    if 1 <= frame['__pc'] < 4:
        while frame['__tmp1__']:
            if frame['__pc'] == 1:
                try:
                    frame['k'] = next(frame['__tmp0__'])
                except StopIteration:
                    frame['__tmp1__'] = False
                    continue
                frame['__pc'] = 2
                return CallOp(func='matrix_chain_mult__helper', args=[frame['i'], frame['k']], kwargs={}, ret_variable='profit')
            if frame['__pc'] == 2:
                frame['__pc'] = 3
                return CallOp(func='matrix_chain_mult__helper', args=[frame['k'] + 1, frame['j']], kwargs={}, ret_variable='__tmp3__')
            if frame['__pc'] == 3:
                frame['profit'] += frame['__tmp3__']
                frame['profit'] += sizes[frame['i'] - 1] * sizes[frame['k']] * sizes[frame['j']]
                frame['max_profit'] = max(frame['max_profit'], frame['profit'])
                frame['__pc'] = 4
            frame['__pc'] = 1
        frame['__pc'] = 4

    if frame['__pc'] == 4:
        frame['__pc'] = 5
        return RetOp(value=frame['max_profit'])


# ------------------------------------


