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
    num_non_defaults = len(args.posonlyargs) + \
        len(args.args) - len(args.defaults)
    args_iter = itertools.chain(iter(args.posonlyargs), iter(args.args))
    for _ in range(num_non_defaults):
        yield next(args_iter), None
    for default in args.defaults:
        yield next(args_iter), default


def bind_frame(positional_args, keyword_args, fn_tree: ast.FunctionDef):
    frame = {}
    # Reverse the list of args because we pop args from the front of the
    # original list, which is the back of the reversed list.
    positional_args, fn_args = list(reversed(positional_args)), fn_tree.args
    for needed_arg, default in pos_with_defaults(fn_args):
        name: str = needed_arg.arg
        if positional_args:  # If we can still take args
            frame[name] = positional_args.pop()
            continue

        if name in keyword_args:
            if needed_arg in fn_tree.args.posonlyargs:
                raise TypeError(
                    f"{fn_tree.name}: got positional only argument {name} as a keyword")
            frame[name] = keyword_args[name]
            del keyword_args[name]
            continue

        elif not default:
            raise TypeError(f"{fn_tree.name} had too few positional arguments")
        frame[name] = default

    if fn_args.vararg:
        # Unreverse the list as from the beginning.
        frame[fn_args.vararg.arg] = list(reversed(positional_args))

    keyword_arg_names = set(k.arg for k in itertools.chain(
        fn_args.args, fn_args.kwonlyargs))
    for kwarg in keyword_args:
        if kwarg not in keyword_arg_names:
            raise TypeError(
                f"{fn_tree.name} got invalid keyword argument '{kwarg}'")
        if kwarg in frame:
            raise TypeError(
                f"{fn_tree.name} got multiple values for argument '{kwarg}'")
        frame[kwarg] = keyword_args[kwarg]

    for kwarg, default in zip(fn_args.kwonlyargs, fn_args.kw_defaults):
        if default is None and kwarg.arg not in frame:
            raise TypeError(
                f"{fn_tree.name} missing required keyword only argument '{kwarg.arg}'")
        if default is not None and kwarg.arg not in frame:
            frame[kwarg.arg] = ast.literal_eval(default)

    frame[jumps.PC_LOCAL_NAME] = 0
    return frame


def run(fn, args=None, kwargs=None, *, __max_stack_size=float('inf')):
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}

    frame = bind_frame(args, kwargs, fiber.FIBER_FN_COMPILED_MAP[fn].fn_def)
    stack: List[StackFrame] = [StackFrame(frame, fn, None)]
    while True:
        assert len(stack) <= __max_stack_size
        top = stack[-1]
        op = top.fn(top.frame)
        if isinstance(op, fiber.CallOp):
            metadata = fiber.FIBER_FN_NAME_MAP[op.func]
            top.ret_variable = op.ret_variable
            frame = bind_frame(op.args, op.kwargs, metadata.fn_def)
            stack.append(StackFrame(frame, metadata.fn, None))
        elif isinstance(op, fiber.TailCallOp):
            stack.pop()  # Tail call, so we can discard the frame.
            metadata = fiber.FIBER_FN_NAME_MAP[op.func]
            frame = bind_frame(op.args, op.kwargs, metadata.fn_def)
            stack.append(StackFrame(frame, metadata.fn, None))
        elif isinstance(op, fiber.RetOp):
            stack.pop()
            if not stack:
                return op.value
            top = stack[-1]
            assert top.ret_variable is not None
            top.frame[top.ret_variable] = op.value
