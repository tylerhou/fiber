import ast
from dataclasses import dataclass
from typing import Any, Dict, List, Union
import itertools

import fiber
import jumps


@dataclass
class StackFrame:
    frame: Dict[str, Any]
    fn: Any
    ret_variable: Union[str, None]

def pos_with_defaults(args: ast.arguments):
    num_non_defaults = len(args.posonlyargs) + len(args.args) - len(args.defaults)
    args_iter = itertools.chain(iter(args.posonlyargs), iter(args.args))
    for _ in range(num_non_defaults):
        yield next(args_iter), None
    for default in args.defaults:
        yield next(args_iter), default

def bind_frame(args, kwargs, fn_tree: ast.FunctionDef):
    # TODO(tylerhou): Fix fib(n-1) + fib(n=n-2)
    frame = {}
    args, fn_args = list(reversed(args)), fn_tree.args
    for arg, default in pos_with_defaults(fn_args):
        if not args:
            if not default:
                raise TypeError(f"{fn_tree.name} had too few positional arguments")
            frame[arg.arg] = default
            continue
        frame[arg.arg] = args.pop()

    if fn_args.vararg:
        frame[fn_args.vararg.arg] = list(reversed(args))

    fn_kwargs = set(k.arg for k in itertools.chain(fn_args.args, fn_args.kwonlyargs))
    for kwarg in kwargs:
        if kwarg not in fn_kwargs:
            raise TypeError(f"{fn_tree.name} got invalid keyword argument '{kwarg}'")
        if kwarg in frame:
            raise TypeError(f"{fn_tree.name} got multiple values for argument '{kwarg.arg}'")
        frame[kwarg] = kwargs[kwarg]

    for kwarg, default in zip(fn_args.kwonlyargs, fn_args.kw_defaults):
        if default is None and kwarg.arg not in frame:
            raise TypeError(f"{fn_tree.name} missing required keyword only argument '{kwarg.arg}'")
        if default is not None and kwarg.arg not in frame:
            frame[kwarg.arg] = ast.literal_eval(default)

    frame[jumps.PC_LOCAL_NAME] = 0
    return frame


def run(fn, args=None, kwargs=None):
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}

    frame = bind_frame(args, kwargs, fiber.FIBER_FUNCTIONS[fn][0])
    stack: List[StackFrame] = [StackFrame(frame, fn, None)]
    while True:
        top = stack[-1]
        op = top.fn(top.frame)
        if isinstance(op, fiber.CallOp):
            fn_tree, fiberfn = fiber.FIBER_FUNCTIONS[op.func]
            top.ret_variable = op.ret_variable
            frame = bind_frame(op.args, op.kwargs, fn_tree)
            stack.append(StackFrame(frame, fiberfn, None))
        elif isinstance(op, fiber.TailCallOp):
            stack.pop()  # Tail call, so we can discard the frame.
            fn_tree, fiberfn = fiber.FIBER_FUNCTIONS[op.func]
            frame = bind_frame(op.args, op.kwargs, fn_tree)
            stack.append(StackFrame(frame, fiberfn, None))
        elif isinstance(op, fiber.RetOp):
            stack.pop()
            if not stack:
                return op.value
            top = stack[-1]
            assert top.ret_variable is not None
            top.frame[top.ret_variable] = op.value
