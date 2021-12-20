# Fiber

Fiber implements an proof-of-concept Python decorator that rewrites a function
so that it can be paused and resumed (by moving stack variables to a heap frame
and adding if statements to simulate jumps/gotos to specific lines of code).

Then, using a trampoline function that simulates the call stack on the heap, we
can call functions that recurse arbitrarily deeply without stack overflowing
(assuming we don't run out of heap memory).

```python3
cache = {}

@fiber.fiber(locals=locals())
def fib(n):
    assert n >= 0
    if n in cache:
        return cache[n]
    if n == 0:
        return 0
    if n == 1:
        return 1
    cache[n] = fib(n-1) + fib(n-2)
    return cache[n]

print(sys.getrecursionlimit())  # 1000 by default

# https://www.wolframalpha.com/input/?i=fib%281010%29+mod+10**5
print(trampoline.run(fib, [1010]) % 10 ** 5) # 74305
```

Please do not use this in production.

## TOC

* [Fiber](#fiber)
   * [How it works](#how-it-works)
   * [Performance](#performance)
   * [Limitations](#limitations)
      * [Possible improvements](#possible-improvements)
   * [Questions](#questions)
      * [Why didn't you use Python generators?](#why-didnt-you-use-python-generators)
      * [Why did you write this?](#why-did-you-write-this)
   * [Contributing](#contributing)
   * [License](#license)
   * [Disclaimer](#disclaimer)

## How it works

A quick refresher on the call stack: normally, when some function A calls
another function B, A is "paused" while B runs to completion. Then, once B
finishes, A is resumed.

In order to move the call stack to the heap, we need to transform function A
to (1) store all variables on the heap, and (2) be able to resume execution
at specific lines of code within the function.

The first step is easy: we rewrite all local loads and stores to instead load
and store in a frame dictionary that is passed into the function. The second is
more difficult: because Python doesn't support goto statements, we have to
insert if statements to skip the code prefix that we don't want to execute.

There are a variety of ["special
forms"](https://www.gnu.org/software/emacs/manual/html_node/elisp/Special-Forms.html)
that cannot be jumped into. These we must handle by rewriting them into a form
that we do handle.

For example, if we recursively call a function inside a for loop, we would like
to be able to resume execution on the same iteration. However, when Python
executes a for loop on an non-iterator iterable it will create a new iterator
every time. To handle this case, we rewrite for loops into the equivalent while
loop. Similarly, we must rewrite boolean expressions that short circuit (`and`,
`or`) into the equivalent if statements.

Lastly, we must replace all recursive calls and normal returns by instead
returning an instruction to a trampoline to call the child function or return
the value to the parent function, respectively.

To recap, here are the AST passes we currently implement:

1. Rewrite special forms:
   - `for_to_while`: Transforms for loops into the equivalent while loops.
   - `promote_while_cond`: Rewrites the while conditional to use a temporary
     variable that is updated every loop iteration so that we can control when
     it is evaluated (e.g. if the loop condition includes a recursive call).
   - `bool_exps_to_if`: Converts `and` and `or` expressions into the
     equivalent if statements.
1. `promote_to_temporary`: Assigns the results of recursive calls into
   temporary variables. This is necessary when we make multiple recursive calls
   in the same statement (e.g. `fib(n-1) + fib(n-2)`): we need to resume
   execution in the middle of the expression.
1. `remove_trivial_temporaries`: Removes temporaries that are assigned to only
   once and are directly assigned to some other variable, replacing subsequent
   usages with that other variable. This helps us detect tail calls.
1. `insert_jumps`: Marks the statement after yield points (currently recursive
   calls and normal returns) with a `pc` index, and inserts if statements so
   that re-execution of the function will resume at that program counter.
1. `lift_locals_to_frame`: Replaces loads and stores of local variables to
   loads and stores in the frame object.
1. `add_trampoline_returns`: Replaces places where we must yield (recursive
   calls and normal returns) with returns to the trampoline function.
1. `fix_fn_def`: Rewrites the function defintion to take a `frame` parameter.

See the [`examples`](examples) directory for functions and the results after
each AST pass. Also, see [`src/trampoline_test.py`](src/trampoline_test.py) for
some test cases.

## Performance

A simple tail-recursive function that computes the sum of an array takes about
10-11 seconds to compute with Fiber. 1000 iterations of the equivalent for loop
takes 7-8 seconds to compute. So we are slower by roughly a factor of 1000.

```python3
lst = list(range(1, 100001))

# fiber
@fiber.fiber(locals=locals())
def sum(lst, acc):
    if not lst:
        return acc
    return sum(lst[1:], acc + lst[0])

# for loop
total = 0
for i in lst:
    total += i

print(total, trampoline.run(sum, [lst, 0]))  # 5000050000, 5000050000
```

We could improve the performance of the code by eliminating redundant if
checks in the generated code. Also, as we statically know the stack variables,
we can use an array for the stack frame and integer indexes (instead of a
dictionary and string hashes + lookups). This should improve the performance
significantly, but there will still probably be a large amount of overhead.

Another performance improvement is to inline the stack array: instead of
storing a list of frames in the trampoline, we could variables directly in the
stack. Again, we can compute the frame size statically. Based on some tests in
a handwritten JavaScript implementation, this has the potential to speed up the
code by roughly a factor of 2-3, at the cost of a more complex implementation.

## Limitations

- The transformation works on the AST level, so we don't support other
  decorators (for example, we cannot use
  [functools.cache](https://docs.python.org/3.10/library/functools.html#functools.cache)
  in the above Fibonacci example).

- The function can only access variables that are passed in the `locals=`
  argument. As a consequence of this, to resolve recursive function calls,
  we maintain a global mapping of all fiber functions by name. This means that
  fibers must have distinct names.

- We don't support some special forms (ternaries, comprehensions). These can
  easily be added as a rewrite transformation.

- We don't support exceptions. This would require us to keep track of exception
  handlers in the trampoline and insert returns to the trampoline to register
  and deregister handlers.

- We don't support generators. To add support, we would have to modify the
  trampoline to accept another operation type (yield) that sends a value to the
  function that called `next()`. Also, the trampoline would have to support
  multiple call stacks.


### Possible improvements

- Improve test coverage on some of the AST transformations.
  - `remove_trivial_temporaries` may have a bug if the variable that it is
    replaced with is reassigned to another value.
- Support more special forms (comprehensions, generators).
- Support exceptions.
- Support recursive calls that don't read the return value.

## Questions

### Why didn't you use Python generators?

It's less interesting as the transformations are easier. Here, we are
effectively implementing generators in userspace (i.e. not needing VM support);
see the answer to the next question for why this is useful.

Also, people have used generators to do this; see [one recent generator
example](https://hurryabit.github.io/blog/stack-safety-for-free/).

### Why did you write this?

- [A+ project for CS 61A at
  Berkeley.](https://web.archive.org/web/20211208153249/https://cs61a.org/articles/about/#a-grades)
  During the course, we created a Scheme interpreter. The extra credit
  question we to replace tail calls in Python with a return to a trampoline,
  with the goal that tail call optimization in Python would let us evaluate
  tail calls to arbitrary depth in Scheme, in constant space.

  The test cases for the question checked whether interpreting tail-call
  recursive functions in Scheme caused a Python stack overflow. Using this
  Fiber implementation, (1) without tail call optimization in our trampoline,
  we would still be able to pass the test cases (we just wouldn't use constant
  space) and (2) we can now evaluate any Scheme expression to arbitrary depth,
  even if they are not in tail form.

- The React framework has an a bug open which explores a compiler transform to
  rewrite JavaScript generators to a state machine so that recursive operations
  (render, reconcilation) can be written more easily. This is necessary because
  some JavaScript engines still don't support generators.

  This project basically implements a rough version of that compiler transform
  as a proof of concept, just in Python.
  https://github.com/facebook/react/pull/18942

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for more details.

## License

Apache 2.0; see [`LICENSE`](LICENSE) for more details.

## Disclaimer

This is a personal project, not an official Google project. It is not supported
by Google and Google specifically disclaims all warranties as to its quality,
merchantability, or fitness for a particular purpose.

