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
    if pc == 0:
        for i in range(10):
            print(hello)
        pc = 1
    if pc == 1:
        a = hello + world
        pc = 2
    if 2 <= pc < 5:
        while b < a:
            if pc == 2:
                print()
                pc = 3
            if pc == 3:
                b = a * a
                pc = 4
            if pc == 4:
                a = a + b
                pc = 5
            pc = 2
        pc = 5
    if 5 <= pc < 7:
        if True:
            if pc == 5:
                d = a + b
                pc = 6
            if pc == 6:
                d = d * 2
                pc = 7
        pc = 7
    if pc == 7:
        d = d + 1
        pc = 8
    if pc == 8:
        d = d + 2
        return d
        pc = 9
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
def fib(pc, n):
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
