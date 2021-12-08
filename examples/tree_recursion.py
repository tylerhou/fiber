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

def all_zeroes(tree):
    if tree == 0:
        return True
    if not isinstance(tree, Tree):
        return False

    return all_zeroes(tree.left) and all_zeroes(tree.right)


# ------------------------------------


# Pass (1): for_to_while

def all_zeroes(tree):
    if tree == 0:
        return True
    if not isinstance(tree, Tree):
        return False

    return all_zeroes(tree.left) and all_zeroes(tree.right)


# ------------------------------------


# Pass (2): promote_while_cond

def all_zeroes(tree):
    if tree == 0:
        return True
    if not isinstance(tree, Tree):
        return False

    return all_zeroes(tree.left) and all_zeroes(tree.right)


# ------------------------------------


# Pass (3): bool_exps_to_if

def all_zeroes(tree):
    if tree == 0:
        return True
    if not isinstance(tree, Tree):
        return False

    __tmp0__ = all_zeroes(tree.left)
    if __tmp0__:
        __tmp0__ = all_zeroes(tree.right)
    return __tmp0__


# ------------------------------------


# Pass (4): promote_to_temporary_m

def all_zeroes(tree):
    if tree == 0:
        return True
    if not isinstance(tree, Tree):
        return False

    __tmp1__ = all_zeroes(tree.left)
    __tmp0__ = __tmp1__
    if __tmp0__:
        __tmp2__ = all_zeroes(tree.right)
        __tmp0__ = __tmp2__
    return __tmp0__


# ------------------------------------


# Pass (5): remove_trivial_temporaries

def all_zeroes(tree):
    if tree == 0:
        return True
    if not isinstance(tree, Tree):
        return False

    __tmp0__ = all_zeroes(tree.left)
    if __tmp0__:
        __tmp0__ = all_zeroes(tree.right)
    return __tmp0__


# ------------------------------------


# Pass (6): insert_jumps

def all_zeroes(tree):
    if __pc == 0:
        if tree == 0:
            if __pc == 0:
                return True
                __pc = 1
        if not isinstance(tree, Tree):
            if __pc == 0:
                return False
                __pc = 1

        __tmp0__ = all_zeroes(tree.left)
        __pc = 1
    if __pc == 1:
        if __tmp0__:
            if __pc == 1:
                __tmp0__ = all_zeroes(tree.right)
                __pc = 2
        __pc = 2
    if __pc == 2:
        return __tmp0__
        __pc = 3


# ------------------------------------


# Pass (7): lift_locals_to_frame

def all_zeroes(tree):
    if frame['__pc'] == 0:
        if frame['tree'] == 0:
            if frame['__pc'] == 0:
                return True
                frame['__pc'] = 1
        if not isinstance(frame['tree'], Tree):
            if frame['__pc'] == 0:
                return False
                frame['__pc'] = 1

        frame['__tmp0__'] = all_zeroes(frame['tree'].left)
        frame['__pc'] = 1
    if frame['__pc'] == 1:
        if frame['__tmp0__']:
            if frame['__pc'] == 1:
                frame['__tmp0__'] = all_zeroes(frame['tree'].right)
                frame['__pc'] = 2
        frame['__pc'] = 2
    if frame['__pc'] == 2:
        return frame['__tmp0__']
        frame['__pc'] = 3


# ------------------------------------


# Pass (8): add_trampoline_returns

def all_zeroes(tree):
    if frame['__pc'] == 0:
        if frame['tree'] == 0:
            if frame['__pc'] == 0:
                frame['__pc'] = 1
                return RetOp(value=True)
        if not isinstance(frame['tree'], Tree):
            if frame['__pc'] == 0:
                frame['__pc'] = 1
                return RetOp(value=False)

        frame['__pc'] = 1
        return CallOp(func='all_zeroes', args=[frame['tree'].left], kwargs={}, ret_variable='__tmp0__')
    if frame['__pc'] == 1:
        if frame['__tmp0__']:
            if frame['__pc'] == 1:
                frame['__pc'] = 2
                return CallOp(func='all_zeroes', args=[frame['tree'].right], kwargs={}, ret_variable='__tmp0__')
        frame['__pc'] = 2
    if frame['__pc'] == 2:
        frame['__pc'] = 3
        return RetOp(value=frame['__tmp0__'])


# ------------------------------------


# Pass (9): fix_fn_def

def __fiberfn_all_zeroes(frame):
    if frame['__pc'] == 0:
        if frame['tree'] == 0:
            if frame['__pc'] == 0:
                frame['__pc'] = 1
                return RetOp(value=True)
        if not isinstance(frame['tree'], Tree):
            if frame['__pc'] == 0:
                frame['__pc'] = 1
                return RetOp(value=False)

        frame['__pc'] = 1
        return CallOp(func='all_zeroes', args=[frame['tree'].left], kwargs={}, ret_variable='__tmp0__')
    if frame['__pc'] == 1:
        if frame['__tmp0__']:
            if frame['__pc'] == 1:
                frame['__pc'] = 2
                return CallOp(func='all_zeroes', args=[frame['tree'].right], kwargs={}, ret_variable='__tmp0__')
        frame['__pc'] = 2
    if frame['__pc'] == 2:
        frame['__pc'] = 3
        return RetOp(value=frame['__tmp0__'])


# ------------------------------------


