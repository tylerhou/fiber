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

def sum(lst, acc):
    if not lst:
        return acc
    return sum(lst[1:], acc + lst[0])


# ------------------------------------


# Pass (1): for_to_while

def sum(lst, acc):
    if not lst:
        return acc
    return sum(lst[1:], acc + lst[0])


# ------------------------------------


# Pass (2): promote_while_cond

def sum(lst, acc):
    if not lst:
        return acc
    return sum(lst[1:], acc + lst[0])


# ------------------------------------


# Pass (3): bool_exps_to_if

def sum(lst, acc):
    if not lst:
        return acc
    return sum(lst[1:], acc + lst[0])


# ------------------------------------


# Pass (4): promote_to_temporary_m

def sum(lst, acc):
    if not lst:
        return acc
    __tmp0__ = sum(lst[1:], acc + lst[0])
    return __tmp0__


# ------------------------------------


# Pass (5): remove_trivial_temporaries

def sum(lst, acc):
    if not lst:
        return acc
    return sum(lst[1:], acc + lst[0])


# ------------------------------------


# Pass (6): insert_jumps

def sum(lst, acc):
    if __pc == 0:
        if not lst:
            if __pc == 0:
                return acc
                __pc = 1
        return sum(lst[1:], acc + lst[0])
        __pc = 1


# ------------------------------------


# Pass (7): lift_locals_to_frame

def sum(lst, acc):
    if frame['__pc'] == 0:
        if not frame['lst']:
            if frame['__pc'] == 0:
                return frame['acc']
                frame['__pc'] = 1
        return sum(frame['lst'][1:], frame['acc'] + frame['lst'][0])
        frame['__pc'] = 1


# ------------------------------------


# Pass (8): add_trampoline_returns

def sum(lst, acc):
    if frame['__pc'] == 0:
        if not frame['lst']:
            if frame['__pc'] == 0:
                frame['__pc'] = 1
                return RetOp(value=frame['acc'])
        frame['__pc'] = 1
        return TailCallOp(func='sum', args=[frame['lst'][1:], frame['acc'] + frame['lst'][0]], kwargs={})


# ------------------------------------


# Pass (9): fix_fn_def

def __fiberfn_sum(frame):
    if frame['__pc'] == 0:
        if not frame['lst']:
            if frame['__pc'] == 0:
                frame['__pc'] = 1
                return RetOp(value=frame['acc'])
        frame['__pc'] = 1
        return TailCallOp(func='sum', args=[frame['lst'][1:], frame['acc'] + frame['lst'][0]], kwargs={})


# ------------------------------------


