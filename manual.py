from dataclasses import dataclass
from typing import Any


def editDistance(first, second):
    """Computes the edit distance between two strings.

    >>> editDistance("kitten", "sitting")
    3
    """

    return editDistanceImpl(first, second, 0, 0)


def editDistanceImpl(first, second, f, s):
    if f == len(first):
        return len(second) - s
    if s == len(second):
        return len(first) - f

    if first[f] == second[s]:
        return editDistanceImpl(first, second, f+1, s+1)

    deleteFirst = editDistanceImpl(first, second, f+1, s) + 1
    deleteSecond = editDistanceImpl(first, second, f, s+1) + 1
    replace = editDistanceImpl(first, second, f+1, s+1) + 1
    return min(deleteFirst, deleteSecond, replace)


@dataclass
class Frame:
    __pc: int
    locals: Any
    child: Any


@dataclass
class CallOp:
    fn: Any
    arguments: Any


@dataclass
class TailCallOp:
    callop: CallOp


@dataclass
class RetOp:
    pass


def engine(fn, args):
    stack = []  # make frame fn, args
    while True:
        # op = run last function on stack
        # if op == tailcall
        # pop the last frame in stack
        # if op == call or tailcall
        # bind arguments to corresponding frame locals
        # push new frame onto stack
        # if op == ret
        # pop last frame in stack
        # if no parent frame, return value
        # assign new top's child frame pointer to popped frame
        # next function will read the return value through the pointer

        # ABI: returns put return value into the current frame
        # We don't support nested functions.


def editDistanceIterImpl(frame):
    if frame.__pc == 0:
        if frame.f == len(frame.first):
            return len(frame.second) - frame.s
        if frame.s == len(frame.second):
            return len(frame.first) - frame.s

    if 0 <= frame.__pc <= 1:
        if frame.first[frame.f] == frame.second[frame.s]:
            if frame.__pc == 0:
                frame.__pc = 1
                # callop editDistanceImpl(frame.first, frame.second, frame.f+1, frame.s+1)
            # jmp (1)
            return frame.child.ret
        frame.__pc = 2

    if frame.__pc == 2:
        frame.__pc = 3
        # callop editDistanceImpl(frame.first, frame.second, frame.f+1, frame.s)
        frame.deleteFirst = frame.child.ret + 1
    # jmp
    if frame.__pc == 3:
        frame.__pc = 4
        # callop editDistanceImpl(frame.first, frame.second, frame.f, frame.s+1)
        frame.deleteSecond = frame.child.ret + 1
    # jmp
    if frame.__pc == 4:
        frame.__pc = 5
        # callop editDistanceImpl(frame.first, frame.second, frame.f+1, frame.s+1)
        frame.replace = frame.child.ret + 1
    # jmp
    if frame.__pc == 5:
        return min(frame.deleteFirst, frame.deleteSecond, frame.replace)

# transforms
# mark recursive calls
# promote nested recursive call results to temporaries
# change locals to accesses in heap frame
# add jump points after recursive calls
# write recursive calls as returning (tail)?call ops
# write returns as returning return ops
# write jumps as if statements & pc counter
