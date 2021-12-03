import ast
import unittest
import transform
import utils


class TestTransform(unittest.TestCase):

    def test_promote_to_temporary(self):
        promote_to_temporary_source = """
def foo():
    t = bar(2)
    if t == 1:
        return bar(bar(bar(1), 3), 5) + bar(baz(t), 4)
    if t == bar(10):
        return bar(baz(t), 2)
        """.strip()

        promote_to_temporary_want = """
def foo():
    t = bar(2)
    if t == 1:
        __$tmp1__ = bar(1)
        __$tmp2__ = bar(__$tmp1__, 3)
        __$tmp3__ = bar(__$tmp2__, 5)
        __$tmp4__ = bar(baz(t), 4)
        return __$tmp3__ + __$tmp4__
    __$tmp5__ = bar(10)
    if t == __$tmp5__:
        return bar(baz(t), 2)
        """.strip()

        tree = ast.parse(promote_to_temporary_source).body[0]
        tree = transform.promote_to_temporary(
            tree, ["bar"], utils.dunder_names())
        tree = ast.fix_missing_locations(tree)
        result = ast.unparse(tree)
        self.assertEqual(result, promote_to_temporary_want)

    def test_for_to_while(self):
        for_to_while_source = """
def bar():
    pre = 1
    for i in range(10):
        print(pre, i)
        if i == 5:
            break
    else:
        print('else')
    post = 1
    return pre + post
        """.strip()

        for_to_while_want = """
def bar():
    pre = 1
    __$tmp0__ = iter(range(10))
    __$tmp1__ = True
    while __$tmp1__:
        try:
            i = next(__$tmp0__)
        except StopIteration:
            __$tmp1__ = False
            continue
        print(pre, i)
        if i == 5:
            break
    else:
        print('else')
    post = 1
    return pre + post
        """.strip()

        tree = ast.parse(for_to_while_source).body[0]
        tree = transform.for_to_while(tree, utils.dunder_names())
        tree = ast.fix_missing_locations(tree)
        result = ast.unparse(tree)
        self.assertEqual(result, for_to_while_want)

    def test_promote_while_cond(self):
        promote_while_cond_source = """
def bar():
    p = [1, 2, 3]
    while len(p) > 0:
        t = p.pop()
    else:
        print('else')
    post = 1
    return t + post
        """.strip()

        promote_while_cond_want = """
def bar():
    p = [1, 2, 3]
    __$tmp0__ = len(p) > 0
    while __$tmp0__:
        t = p.pop()
        __$tmp0__ = len(p) > 0
    else:
        print('else')
    post = 1
    return t + post
        """.strip()

        tree = ast.parse(promote_while_cond_source).body[0]
        tree = transform.promote_while_cond(tree, utils.dunder_names())
        tree = ast.fix_missing_locations(tree)
        result = ast.unparse(tree)
        self.assertEqual(result, promote_while_cond_want)


if __name__ == '__main__':
    unittest.main()
