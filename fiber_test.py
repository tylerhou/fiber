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
def __fiberfn_fib(frame):
    if frame['__pc'] == 0:
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
        return CallOp(func='fib', args=[], kwargs={'n': frame['n'] - 2}, ret_variable='__tmp1__')
    if frame['__pc'] == 2:
        frame['__pc'] = 3
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
def __fiberfn_sum(frame):
    if frame['__pc'] == 0:
        if not frame['lst']:
            if frame['__pc'] == 0:
                frame['__pc'] = 1
                return RetOp(value=frame['acc'])
        frame['__pc'] = 1
        return TailCallOp(func='sum', args=[frame['lst'][1:], frame['acc'] + frame['lst'][0]], kwargs={})
        """.strip()
        self.assertEqual(want, sum.__fibercode__)


if __name__ == '__main__':
    unittest.main()
