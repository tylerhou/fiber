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

def fib(n):
    if n in cache:
        return cache[n]

    if n == 0:
        return 0
    if n == 1:
        return 1

    cache[n] = fib(n - 1) + fib(n - 2)
    return cache[n]


# ------------------------------------


# Pass (1): for_to_while

def fib(n):
    if n in cache:
        return cache[n]

    if n == 0:
        return 0
    if n == 1:
        return 1

    cache[n] = fib(n - 1) + fib(n - 2)
    return cache[n]


# ------------------------------------


# Pass (2): promote_while_cond

def fib(n):
    if n in cache:
        return cache[n]

    if n == 0:
        return 0
    if n == 1:
        return 1

    cache[n] = fib(n - 1) + fib(n - 2)
    return cache[n]


# ------------------------------------


# Pass (3): bool_exps_to_if

def fib(n):
    if n in cache:
        return cache[n]

    if n == 0:
        return 0
    if n == 1:
        return 1

    cache[n] = fib(n - 1) + fib(n - 2)
    return cache[n]


# ------------------------------------


# Pass (4): promote_to_temporary_m

def fib(n):
    if n in cache:
        return cache[n]

    if n == 0:
        return 0
    if n == 1:
        return 1

    __tmp0__ = fib(n - 1)
    __tmp1__ = fib(n - 2)

    cache[n] = __tmp0__ + __tmp1__
    return cache[n]


# ------------------------------------


# Pass (5): remove_trivial_temporaries

def fib(n):
    if n in cache:
        return cache[n]

    if n == 0:
        return 0
    if n == 1:
        return 1

    __tmp0__ = fib(n - 1)
    __tmp1__ = fib(n - 2)

    cache[n] = __tmp0__ + __tmp1__
    return cache[n]


# ------------------------------------


# Pass (6): insert_jumps

def fib(n):
    if __pc == 0:
        if n in cache:
            if __pc == 0:
                return cache[n]
                __pc = 1

        if n == 0:
            if __pc == 0:
                return 0
                __pc = 1
        if n == 1:
            if __pc == 0:
                return 1
                __pc = 1

        __tmp0__ = fib(n - 1)
        __pc = 1
    if __pc == 1:
        __tmp1__ = fib(n - 2)
        __pc = 2

    if __pc == 2:
        cache[n] = __tmp0__ + __tmp1__
        return cache[n]
        __pc = 3


# ------------------------------------


# Pass (7): lift_locals_to_frame

def fib(n):
    if frame['__pc'] == 0:
        if frame['n'] in cache:
            if frame['__pc'] == 0:
                return cache[frame['n']]
                frame['__pc'] = 1

        if frame['n'] == 0:
            if frame['__pc'] == 0:
                return 0
                frame['__pc'] = 1
        if frame['n'] == 1:
            if frame['__pc'] == 0:
                return 1
                frame['__pc'] = 1

        frame['__tmp0__'] = fib(frame['n'] - 1)
        frame['__pc'] = 1
    if frame['__pc'] == 1:
        frame['__tmp1__'] = fib(frame['n'] - 2)
        frame['__pc'] = 2

    if frame['__pc'] == 2:
        cache[frame['n']] = frame['__tmp0__'] + frame['__tmp1__']
        return cache[frame['n']]
        frame['__pc'] = 3


# ------------------------------------


# Pass (8): add_trampoline_returns

def fib(n):
    if frame['__pc'] == 0:
        if frame['n'] in cache:
            if frame['__pc'] == 0:
                frame['__pc'] = 1
                return RetOp(value=cache[frame['n']])

        if frame['n'] == 0:
            if frame['__pc'] == 0:
                frame['__pc'] = 1
                return RetOp(value=0)
        if frame['n'] == 1:
            if frame['__pc'] == 0:
                frame['__pc'] = 1
                return RetOp(value=1)

        frame['__pc'] = 1
        return CallOp(func='fib', args=[frame['n'] - 1], kwargs={}, ret_variable='__tmp0__')
    if frame['__pc'] == 1:
        frame['__pc'] = 2
        return CallOp(func='fib', args=[frame['n'] - 2], kwargs={}, ret_variable='__tmp1__')

    if frame['__pc'] == 2:
        cache[frame['n']] = frame['__tmp0__'] + frame['__tmp1__']
        frame['__pc'] = 3
        return RetOp(value=cache[frame['n']])


# ------------------------------------


# Pass (9): fix_fn_def

def __fiberfn_fib(frame):
    if frame['__pc'] == 0:
        if frame['n'] in cache:
            if frame['__pc'] == 0:
                frame['__pc'] = 1
                return RetOp(value=cache[frame['n']])

        if frame['n'] == 0:
            if frame['__pc'] == 0:
                frame['__pc'] = 1
                return RetOp(value=0)
        if frame['n'] == 1:
            if frame['__pc'] == 0:
                frame['__pc'] = 1
                return RetOp(value=1)

        frame['__pc'] = 1
        return CallOp(func='fib', args=[frame['n'] - 1], kwargs={}, ret_variable='__tmp0__')
    if frame['__pc'] == 1:
        frame['__pc'] = 2
        return CallOp(func='fib', args=[frame['n'] - 2], kwargs={}, ret_variable='__tmp1__')

    if frame['__pc'] == 2:
        cache[frame['n']] = frame['__tmp0__'] + frame['__tmp1__']
        frame['__pc'] = 3
        return RetOp(value=cache[frame['n']])


# ------------------------------------


