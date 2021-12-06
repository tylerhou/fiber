import unittest

import fiber
import trampoline

class TestTrampoline(unittest.TestCase):

    def test_fib(self):
        @fiber.fiber()
        def fib(n):
            if n == 0:
                return 0
            if n == 1:
                return 1
            return fib(n-1) + fib(n-2)
        self.assertEqual(55, trampoline.run(fib, [10], {}))

    def test_sum(self):
        @fiber.fiber()
        def sum(lst, acc):
            if not lst:
                return acc
            return sum(lst[1:], acc + lst[0])
        n = 1000
        want = n * (n + 1) / 2
        got = trampoline.run(sum, [list(range(1, n+1)), 0])
        self.assertEqual(want, got)

    def test_recursion_exceeded(self):
        def sum(lst, acc):
            if not lst:
                return acc
            return sum(lst[1:], acc + lst[0])
        n = 1000
        self.assertRaises(RecursionError, sum, list(range(1, n+1)), 0)


if __name__ == '__main__':
    unittest.main()
