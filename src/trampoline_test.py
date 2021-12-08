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

    def test_edit_distance(self):
        def edit_distance(first, second):
            @fiber.fiber(locals=locals())
            def edit_distance__helper(f, s):
                if f == len(first):
                    return len(second) - s
                if s == len(second):
                    return len(first) - f

                if first[f] == second[s]:
                    return edit_distance__helper(f+1, s+1)

                del_f = edit_distance__helper(f+1, s) + 1
                replace = edit_distance__helper(f+1, s+1) + 1
                del_s = edit_distance__helper(f, s+1) + 1

                return min(del_f, replace, del_s)

            return trampoline.run(edit_distance__helper, [0, 0])
        self.assertEqual(3, edit_distance("kitten", "sitting"))

    def test_pop_balloons(self):
        def pop_balloons(balloons):
            balloons = [1] + balloons + [1]

            @fiber.fiber(locals=locals())
            def pop_balloons__helper(i, j):
                if i == j:
                    return 0
                max_profit = float('-inf')
                for k in range(i, j):
                    profit = pop_balloons__helper(i, k)
                    profit += pop_balloons__helper(k+1, j)
                    profit += balloons[i-1] * balloons[k] * balloons[j]
                    max_profit = max(max_profit, profit)
                return max_profit

            return trampoline.run(pop_balloons__helper, [1, len(balloons) - 1])
        self.assertEqual(175, pop_balloons([4, 5, 7]))

    def test_tree_recursion(self):
        from collections import namedtuple
        Tree = namedtuple("Tree", ["left", "right"])

        @fiber.fiber(locals=locals())
        def all_zeroes(tree):
            if tree == 0:
                return True
            if not isinstance(tree, Tree):
                return False
            return all_zeroes(tree.left) and all_zeroes(tree.right)

        zeroes = Tree(Tree(0, 0), Tree(Tree(Tree(0, 0), 0), Tree(0, 0)))
        one = Tree(Tree(0, 0), Tree(Tree(Tree(1, 0), 0), Tree(0, 0)))
        self.assertTrue(trampoline.run(all_zeroes, [zeroes]))
        self.assertFalse(trampoline.run(all_zeroes, [one]))


if __name__ == '__main__':
    unittest.main()
