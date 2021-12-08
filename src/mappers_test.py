import ast
import unittest
import mappers
import utils


def map_function(source, mapper):
    tree = ast.parse(source).body[0]
    tree = mappers.map_scope(tree, mapper)
    tree = ast.fix_missing_locations(tree)
    return ast.unparse(tree)


class TestMappers(unittest.TestCase):

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

        mapper = mappers.promote_to_temporary_m(["bar"], utils.dunder_names())
        result = map_function(source, mapper)
        self.assertEqual(result, want)

    def test_remove_trivial_temporaries_m(self):
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
        mapper = mappers.remove_trivial_temporaries_m(tree)
        tree = mappers.map_scope(tree, mapper)
        tree = ast.fix_missing_locations(tree)
        result = ast.unparse(tree)
        self.assertEqual(result, want)

    def test_remove_trivial_temporaries_m_tail_call(self):
        source = """
def sum(lst, acc):
    if not lst:
        return acc
    __tmp0__ = sum(lst[1:], acc + lst[0])
    return __tmp0__
        """.strip()

        want = """
def sum(lst, acc):
    if not lst:
        return acc
    return sum(lst[1:], acc + lst[0])
        """.strip()
        tree = ast.parse(source).body[0]
        mapper = mappers.remove_trivial_temporaries_m(tree)
        tree = mappers.map_scope(tree, mapper)
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

        mapper = mappers.for_to_while_m(utils.dunder_names())
        result = map_function(source, mapper)
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

        mapper = mappers.promote_while_cond_m(utils.dunder_names())
        result = map_function(source, mapper)
        self.assertEqual(result, want)

    def test_bool_exps_to_if_m(self):
        source = """
def bar():
    a = first() and (second() or third()) and fourth()
    b = 1 + (foo() or baz())
    return a or b
        """.strip()

        want = """
def bar():
    __tmp0__ = first()
    if __tmp0__:
        __tmp1__ = second()
        if not __tmp1__:
            __tmp1__ = third()
        __tmp0__ = __tmp1__
    if __tmp0__:
        __tmp0__ = fourth()
    a = __tmp0__
    __tmp2__ = foo()
    if not __tmp2__:
        __tmp2__ = baz()
    b = 1 + __tmp2__
    __tmp3__ = a
    if not __tmp3__:
        __tmp3__ = b
    return __tmp3__
        """.strip()

        mapper = mappers.bool_exps_to_if_m(utils.dunder_names())
        result = map_function(source, mapper)
        self.assertEqual(result, want)

    def test_lift_to_frame_m(self):
        source = """
def bar(arg1, arg2):
    a = arg1 + arg2
    if a == 2:
        return arg1 + arg2
    b = a + (foo() or baz())
    return a + b
        """.strip()

        want = """
def bar(arg1, arg2):
    frame['a'] = frame['arg1'] + frame['arg2']
    if frame['a'] == 2:
        return frame['arg1'] + frame['arg2']
    frame['b'] = frame['a'] + (foo() or baz())
    return frame['a'] + frame['b']
        """.strip()
        mapper = mappers.lift_to_frame_m(
            lambda x: x if x in ("a", "b", "arg1", "arg2") else None)
        result = map_function(source, mapper)
        self.assertEqual(result, want)


if __name__ == '__main__':
    unittest.main()
