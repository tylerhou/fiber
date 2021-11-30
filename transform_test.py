import ast
import unittest
import transform
import utils

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

rewrite_for_source = """
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

rewrite_for_want = """
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


class TestTransform(unittest.TestCase):

    def test_promote_to_temporary(self):
        tree = ast.parse(promote_to_temporary_source).body[0]
        tree = transform.promote_to_temporary(
            tree, ["bar"], utils.dunder_names())
        tree = ast.fix_missing_locations(tree)
        result = ast.unparse(tree)
        self.assertEqual(result, promote_to_temporary_want)

    def test_rewrite_for(self):
        tree = ast.parse(rewrite_for_source).body[0]
        tree = transform.rewrite_for(tree, utils.dunder_names())
        tree = ast.fix_missing_locations(tree)
        result = ast.unparse(tree)
        self.assertEqual(result, rewrite_for_want)


if __name__ == '__main__':
    unittest.main()
