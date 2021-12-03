import ast
import unittest
import transform
import utils

def transform_function(source, mapper):
        tree = ast.parse(source).body[0]
        tree = utils.map_scope(tree, mapper)
        tree = ast.fix_missing_locations(tree)
        return ast.unparse(tree)

class TestTransform(unittest.TestCase):

    def test_promote_to_temporary_m(self):
        source = """
def foo():
    t = bar(2)
    if t == 1:
        return bar(bar(bar(1), 3), 5) + bar(baz(t), 4)
    if t == bar(10):
        return bar(baz(t), 2)
        """.strip()

        want = """
def foo():
    __tmp0__ = bar(2)
    t = __tmp0__
    if t == 1:
        __tmp1__ = bar(1)
        __tmp2__ = bar(__tmp1__, 3)
        __tmp3__ = bar(__tmp2__, 5)
        __tmp4__ = bar(baz(t), 4)
        return __tmp3__ + __tmp4__
    __tmp5__ = bar(10)
    if t == __tmp5__:
        __tmp6__ = bar(baz(t), 2)
        return __tmp6__
        """.strip()

        mapper = transform.promote_to_temporary_m(["bar"], utils.dunder_names())
        result = transform_function(source, mapper)
        self.assertEqual(result, want)

    def test_remove_trivial_m(self):
        source = """
def foo():
    __tmp0__ = bar(2)
    t = __tmp0__
    if t == 1:
        __tmp1__ = bar(1)
        __tmp2__ = bar(__tmp1__, 3)
        __tmp3__ = bar(__tmp2__, 5)
        __tmp4__ = bar(baz(t), 4)
        return __tmp3__ + __tmp4__
    __tmp5__ = bar(10)
    if t == __tmp5__:
        __tmp6__ = bar(baz(t), 2)
        return __tmp6__
        """.strip()

        want = """
def foo():
    t = bar(2)
    if t == 1:
        __tmp1__ = bar(1)
        __tmp2__ = bar(__tmp1__, 3)
        __tmp3__ = bar(__tmp2__, 5)
        __tmp4__ = bar(baz(t), 4)
        return __tmp3__ + __tmp4__
    __tmp5__ = bar(10)
    if t == __tmp5__:
        return bar(baz(t), 2)
        """.strip()

        tree = ast.parse(source).body[0]
        # Remove trivial needs to preprocess the tree to find trivial variables.
        mapper = transform.remove_trivial_m(tree)
        tree = utils.map_scope(tree, mapper)
        tree = ast.fix_missing_locations(tree)
        result = ast.unparse(tree)
        self.assertEqual(result, want)

    def test_for_to_while_m(self):
        source = """
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

        want = """
def bar():
    pre = 1
    __tmp0__ = iter(range(10))
    __tmp1__ = True
    while __tmp1__:
        try:
            i = next(__tmp0__)
        except StopIteration:
            __tmp1__ = False
            continue
        print(pre, i)
        if i == 5:
            break
    else:
        print('else')
    post = 1
    return pre + post
        """.strip()

        mapper = transform.for_to_while_m(utils.dunder_names())
        result = transform_function(source, mapper)
        self.assertEqual(result, want)

    def test_promote_while_cond_m(self):
        source = """
def bar():
    p = [1, 2, 3]
    while len(p) > 0:
        t = p.pop()
    else:
        print('else')
    post = 1
    return t + post
        """.strip()

        want = """
def bar():
    p = [1, 2, 3]
    __tmp0__ = len(p) > 0
    while __tmp0__:
        t = p.pop()
        __tmp0__ = len(p) > 0
    else:
        print('else')
    post = 1
    return t + post
        """.strip()

        mapper = transform.promote_while_cond_m(utils.dunder_names())
        result = transform_function(source, mapper)
        self.assertEqual(result, want)


if __name__ == '__main__':
    unittest.main()
