import sys
import unittest

import fiber
import trampoline


class TestTrampoline(unittest.TestCase):

    def test_fib(self):
        cache = {}

        @fiber.fiber(locals=locals())
        def fib(n):
            if n in cache:
                return cache[n]
            if n == 0:
                return 0
            if n == 1:
                return 1
            cache[n] = fib(n-1) + fib(n=n-2)
            return cache[n]
        self.assertEqual(55, trampoline.run(fib, [10], {}))
        self.assertLess(0, trampoline.run(fib, [1002], {}))

    def test_sum(self):
        @fiber.fiber(locals=locals())
        def sum(lst, acc):
            if not lst:
                return acc
            return sum(lst[1:], acc + lst[0])
        n = sys.getrecursionlimit() + 1
        n = 10000
        want = n * (n + 1) / 2
        got = trampoline.run(sum, [list(range(1, n+1)), 0], __max_stack_size=1)
        self.assertEqual(want, got)

    def test_sum_recursion_exceeded(self):
        def sum(lst, acc):
            if not lst:
                return acc
            return sum(lst[1:], acc + lst[0])
        n = sys.getrecursionlimit() + 1
        self.assertRaises(RecursionError, sum, list(range(1, n+1)), 0)

    def test_sum_non_tailcall(self):
        @fiber.fiber(locals=locals())
        def sum(lst, acc):
            if not lst:
                return acc
            return sum(lst[1:], acc + lst[0]) + 1
        n = sys.getrecursionlimit() + 1
        want = n * (n + 1) / 2 + n
        got = trampoline.run(sum, [list(range(1, n+1)), 0])
        self.assertEqual(want, got)

    def test_mutual_recursion(self):
        @fiber.fiber(["b"], locals=locals())
        def a(n):
            if n == 0:
                return 1
            return b(n-1) * 2

        @fiber.fiber(locals=locals())
        def b(n):
            if n == 0:
                return 1
            return a(n-1) * 3
        got = trampoline.run(a, [10])
        self.assertEqual(2**5 * 3**5, got)


if __name__ == '__main__':
    unittest.main()
