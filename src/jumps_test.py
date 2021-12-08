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

import ast
import unittest

import jumps


class TestInsertJumps(unittest.TestCase):

    def test_complex(self):
        source = """
def bar(hello, world):
    for i in range(10):
        print(hello)
    a = hello + world
    while b < a:
        print()
        b = a * a
        a = a + b
    if True:
        d = a + b
        d = d * 2
    d = d + 1
    d = d + 2
    return d
        """.strip()

        want = """
def bar(hello, world):
    if __pc == 0:
        for i in range(10):
            print(hello)
        __pc = 1
    if __pc == 1:
        a = hello + world
        __pc = 2
    if 2 <= __pc < 5:
        while b < a:
            if __pc == 2:
                print()
                __pc = 3
            if __pc == 3:
                b = a * a
                __pc = 4
            if __pc == 4:
                a = a + b
                __pc = 5
            __pc = 2
        __pc = 5
    if 5 <= __pc < 7:
        if True:
            if __pc == 5:
                d = a + b
                __pc = 6
            if __pc == 6:
                d = d * 2
                __pc = 7
        __pc = 7
    if __pc == 7:
        d = d + 1
        __pc = 8
    if __pc == 8:
        d = d + 2
        return d
        __pc = 9
        """.strip()

        tree = ast.parse(source)
        fn_tree = tree.body[0]
        assert isinstance(fn_tree, ast.FunctionDef)
        fn_tree.body, _ = jumps.insert_jumps(
            fn_tree.body, lambda stmt: isinstance(stmt, ast.Assign))
        tree = ast.fix_missing_locations(tree)
        result = ast.unparse(tree)
        self.assertEqual(result, want)

    def test_equivalent(self):
        source = """
def fib(__pc, n):
    curr = 0
    next = 1
    for i in range(n):
        tmp = curr
        curr = next
        next = tmp + next
    return curr
"""

        tree = ast.parse(source)
        fn_tree = tree.body[0]
        assert isinstance(fn_tree, ast.FunctionDef)
        fn_tree.body, _ = jumps.insert_jumps(
            fn_tree.body, lambda stmt: isinstance(stmt, ast.Assign))
        fn_tree.name = "fib_transformed"

        tree = ast.fix_missing_locations(tree)
        code = compile(tree, "<string>", "exec")
        results = {}
        exec(code, globals(), results)
        exec(source, globals(), results)
        fib, fib_transformed = results["fib"], results["fib_transformed"]
        for i in range(100):
            self.assertEqual(fib(0, i), fib_transformed(0, i))


if __name__ == '__main__':
    unittest.main()
