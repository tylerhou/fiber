import ast
import unittest
import transform

source = """
def foo():
    t = bar(2)
    if t == 1:
        return bar(bar(bar(1), 3), 5) + bar(baz(t), 4)
    if t == bar(10):
        return bar(baz(t), 2) + 1
""".strip()

want = """
def foo():
    __$tmp0__ = bar(2)
    t = __$tmp0__
    if t == 1:
        __$tmp1__ = bar(1)
        __$tmp2__ = bar(__$tmp1__, 3)
        __$tmp3__ = bar(__$tmp2__, 5)
        __$tmp4__ = bar(baz(t), 4)
        return __$tmp3__ + __$tmp4__
    __$tmp5__ = bar(10)
    if t == __$tmp5__:
        __$tmp6__ = bar(baz(t), 2)
        return __$tmp6__ + 1
""".strip()


class TestTransform(unittest.TestCase):
    def test_promote_to_temporary(self):
        tree = ast.parse(source).body[0]
        tree = transform.promote_to_temporary(tree, ["bar"])
        tree = ast.fix_missing_locations(tree)
        result = ast.unparse(tree)
        self.assertEqual(result, want)


if __name__ == '__main__':
    unittest.main()
