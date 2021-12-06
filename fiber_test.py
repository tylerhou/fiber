import unittest

import fiber


class TestFiber(unittest.TestCase):

    def test_fib(self):
        @fiber.fiber()
        def fib(n):
            if n == 0:
                return 0
            if n == 1:
                return 1
            return fib(n-1) + fib(n=n-2)
        self.maxDiff = None

        want = """
def __fiberfn_fib(frame, pc=0):
    if pc == 0:
        if frame['n'] == 0:
            if pc == 0:
                pc = 1
                return RetOp(value=0)
        if frame['n'] == 1:
            if pc == 0:
                pc = 1
                return RetOp(value=1)
        pc = 1
        return CallOp(func='fib', args=[frame['n'] - 1], keywords={}, variable='__tmp0__')
    if pc == 1:
        pc = 2
        return CallOp(func='fib', args=[], keywords={'n': frame['n'] - 2}, variable='__tmp1__')
    if pc == 2:
        pc = 3
        return RetOp(value=frame['__tmp0__'] + frame['__tmp1__'])
        """.strip()
        self.assertEqual(want, fib.__fibercode__)

    def test_sum(self):
        @fiber.fiber()
        def sum(lst, acc):
            if not lst:
                return acc
            return sum(lst[1:], acc + lst[0])

        want = """
def __fiberfn_sum(frame, pc=0):
    if pc == 0:
        if not frame['lst']:
            if pc == 0:
                pc = 1
                return RetOp(value=frame['acc'])
        pc = 1
        return TailCallOp(func='sum', args=[frame['lst'][1:], frame['acc'] + frame['lst'][0]], keywords={})
        """.strip()
        self.assertEqual(want, sum.__fibercode__)
