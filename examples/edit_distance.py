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

def edit_distance__helper(f, s):
    if f == len(first):
        return len(second) - s
    if s == len(second):
        return len(first) - f

    if first[f] == second[s]:
        return edit_distance__helper(f + 1, s + 1)

    del_f = edit_distance__helper(f + 1, s) + 1
    replace = edit_distance__helper(f + 1, s + 1) + 1
    del_s = edit_distance__helper(f, s + 1) + 1

    return min(del_f, replace, del_s)


# ------------------------------------


# Pass (1): for_to_while

def edit_distance__helper(f, s):
    if f == len(first):
        return len(second) - s
    if s == len(second):
        return len(first) - f

    if first[f] == second[s]:
        return edit_distance__helper(f + 1, s + 1)

    del_f = edit_distance__helper(f + 1, s) + 1
    replace = edit_distance__helper(f + 1, s + 1) + 1
    del_s = edit_distance__helper(f, s + 1) + 1

    return min(del_f, replace, del_s)


# ------------------------------------


# Pass (2): promote_while_cond

def edit_distance__helper(f, s):
    if f == len(first):
        return len(second) - s
    if s == len(second):
        return len(first) - f

    if first[f] == second[s]:
        return edit_distance__helper(f + 1, s + 1)

    del_f = edit_distance__helper(f + 1, s) + 1
    replace = edit_distance__helper(f + 1, s + 1) + 1
    del_s = edit_distance__helper(f, s + 1) + 1

    return min(del_f, replace, del_s)


# ------------------------------------


# Pass (3): bool_exps_to_if

def edit_distance__helper(f, s):
    if f == len(first):
        return len(second) - s
    if s == len(second):
        return len(first) - f

    if first[f] == second[s]:
        return edit_distance__helper(f + 1, s + 1)

    del_f = edit_distance__helper(f + 1, s) + 1
    replace = edit_distance__helper(f + 1, s + 1) + 1
    del_s = edit_distance__helper(f, s + 1) + 1

    return min(del_f, replace, del_s)


# ------------------------------------


# Pass (4): promote_to_temporary_m

def edit_distance__helper(f, s):
    if f == len(first):
        return len(second) - s
    if s == len(second):
        return len(first) - f

    if first[f] == second[s]:
        __tmp0__ = edit_distance__helper(f + 1, s + 1)
        return __tmp0__

    __tmp1__ = edit_distance__helper(f + 1, s)
    del_f = __tmp1__ + 1
    __tmp2__ = edit_distance__helper(f + 1, s + 1)
    replace = __tmp2__ + 1
    __tmp3__ = edit_distance__helper(f, s + 1)
    del_s = __tmp3__ + 1

    return min(del_f, replace, del_s)


# ------------------------------------


# Pass (5): remove_trivial_temporaries

def edit_distance__helper(f, s):
    if f == len(first):
        return len(second) - s
    if s == len(second):
        return len(first) - f

    if first[f] == second[s]:
        return edit_distance__helper(f + 1, s + 1)

    __tmp1__ = edit_distance__helper(f + 1, s)
    del_f = __tmp1__ + 1
    __tmp2__ = edit_distance__helper(f + 1, s + 1)
    replace = __tmp2__ + 1
    __tmp3__ = edit_distance__helper(f, s + 1)
    del_s = __tmp3__ + 1

    return min(del_f, replace, del_s)


# ------------------------------------


# Pass (6): insert_jumps

def edit_distance__helper(f, s):
    if __pc == 0:
        if f == len(first):
            if __pc == 0:
                return len(second) - s
                __pc = 1
        if s == len(second):
            if __pc == 0:
                return len(first) - f
                __pc = 1

        if first[f] == second[s]:
            if __pc == 0:
                return edit_distance__helper(f + 1, s + 1)
                __pc = 1
        __pc = 1

    if __pc == 1:
        __tmp1__ = edit_distance__helper(f + 1, s)
        __pc = 2
    if __pc == 2:
        del_f = __tmp1__ + 1
        __tmp2__ = edit_distance__helper(f + 1, s + 1)
        __pc = 3
    if __pc == 3:
        replace = __tmp2__ + 1
        __tmp3__ = edit_distance__helper(f, s + 1)
        __pc = 4

    if __pc == 4:
        del_s = __tmp3__ + 1
        return min(del_f, replace, del_s)
        __pc = 5


# ------------------------------------


# Pass (7): lift_locals_to_frame

def edit_distance__helper(f, s):
    if frame['__pc'] == 0:
        if frame['f'] == len(first):
            if frame['__pc'] == 0:
                return len(second) - frame['s']
                frame['__pc'] = 1
        if frame['s'] == len(second):
            if frame['__pc'] == 0:
                return len(first) - frame['f']
                frame['__pc'] = 1

        if first[frame['f']] == second[frame['s']]:
            if frame['__pc'] == 0:
                return edit_distance__helper(frame['f'] + 1, frame['s'] + 1)
                frame['__pc'] = 1
        frame['__pc'] = 1

    if frame['__pc'] == 1:
        frame['__tmp1__'] = edit_distance__helper(frame['f'] + 1, frame['s'])
        frame['__pc'] = 2
    if frame['__pc'] == 2:
        frame['del_f'] = frame['__tmp1__'] + 1
        frame['__tmp2__'] = edit_distance__helper(frame['f'] + 1, frame['s'] + 1)
        frame['__pc'] = 3
    if frame['__pc'] == 3:
        frame['replace'] = frame['__tmp2__'] + 1
        frame['__tmp3__'] = edit_distance__helper(frame['f'], frame['s'] + 1)
        frame['__pc'] = 4

    if frame['__pc'] == 4:
        frame['del_s'] = frame['__tmp3__'] + 1
        return min(frame['del_f'], frame['replace'], frame['del_s'])
        frame['__pc'] = 5


# ------------------------------------


# Pass (8): add_trampoline_returns

def edit_distance__helper(f, s):
    if frame['__pc'] == 0:
        if frame['f'] == len(first):
            if frame['__pc'] == 0:
                frame['__pc'] = 1
                return RetOp(value=len(second) - frame['s'])
        if frame['s'] == len(second):
            if frame['__pc'] == 0:
                frame['__pc'] = 1
                return RetOp(value=len(first) - frame['f'])

        if first[frame['f']] == second[frame['s']]:
            if frame['__pc'] == 0:
                frame['__pc'] = 1
                return TailCallOp(func='edit_distance__helper', args=[frame['f'] + 1, frame['s'] + 1], kwargs={})
        frame['__pc'] = 1

    if frame['__pc'] == 1:
        frame['__pc'] = 2
        return CallOp(func='edit_distance__helper', args=[frame['f'] + 1, frame['s']], kwargs={}, ret_variable='__tmp1__')
    if frame['__pc'] == 2:
        frame['del_f'] = frame['__tmp1__'] + 1
        frame['__pc'] = 3
        return CallOp(func='edit_distance__helper', args=[frame['f'] + 1, frame['s'] + 1], kwargs={}, ret_variable='__tmp2__')
    if frame['__pc'] == 3:
        frame['replace'] = frame['__tmp2__'] + 1
        frame['__pc'] = 4
        return CallOp(func='edit_distance__helper', args=[frame['f'], frame['s'] + 1], kwargs={}, ret_variable='__tmp3__')

    if frame['__pc'] == 4:
        frame['del_s'] = frame['__tmp3__'] + 1
        frame['__pc'] = 5
        return RetOp(value=min(frame['del_f'], frame['replace'], frame['del_s']))


# ------------------------------------


# Pass (9): fix_fn_def

def __fiberfn_edit_distance__helper(frame):
    if frame['__pc'] == 0:
        if frame['f'] == len(first):
            if frame['__pc'] == 0:
                frame['__pc'] = 1
                return RetOp(value=len(second) - frame['s'])
        if frame['s'] == len(second):
            if frame['__pc'] == 0:
                frame['__pc'] = 1
                return RetOp(value=len(first) - frame['f'])

        if first[frame['f']] == second[frame['s']]:
            if frame['__pc'] == 0:
                frame['__pc'] = 1
                return TailCallOp(func='edit_distance__helper', args=[frame['f'] + 1, frame['s'] + 1], kwargs={})
        frame['__pc'] = 1

    if frame['__pc'] == 1:
        frame['__pc'] = 2
        return CallOp(func='edit_distance__helper', args=[frame['f'] + 1, frame['s']], kwargs={}, ret_variable='__tmp1__')
    if frame['__pc'] == 2:
        frame['del_f'] = frame['__tmp1__'] + 1
        frame['__pc'] = 3
        return CallOp(func='edit_distance__helper', args=[frame['f'] + 1, frame['s'] + 1], kwargs={}, ret_variable='__tmp2__')
    if frame['__pc'] == 3:
        frame['replace'] = frame['__tmp2__'] + 1
        frame['__pc'] = 4
        return CallOp(func='edit_distance__helper', args=[frame['f'], frame['s'] + 1], kwargs={}, ret_variable='__tmp3__')

    if frame['__pc'] == 4:
        frame['del_s'] = frame['__tmp3__'] + 1
        frame['__pc'] = 5
        return RetOp(value=min(frame['del_f'], frame['replace'], frame['del_s']))


# ------------------------------------


