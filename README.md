![pcd][0]

Python Contract Decorators
==========================

- [Abstract](#abstract)
- [Install](#install)
- [Documentation](#documentation)
- [Performance](#performance)
- [Testing](#testing)
- [License](#license)


Abstract
--------

Contract programming can be an amazing performance boost, code hardening
technique and self-documentation-level increase at the same time.  The main idea
is that all components in a program could and should *agree* on what they are
passing to each other, or as we call it, they *sign a contract* between each
other.  So instead of having isolated components, which all have to guarantee
their own correctness, the program guarantees the correctness of all of its
components' correct behaviour when those are working together.

Though Python is not supporting contracts natively as a language feature, there
are several libraries out there which try to add the same functionality to
Python, but they are either broken, incomplete, heavy or simply just reinventing
the wheel by introducing foreign syntax to Python.  Fortunately there is almost
always a light and easy way to do things in Python, and that's what `pcd` is
offering.

Anyway, enough abstract mumbo-jumbo, let's start talking about how it works,
shall we?  As usual, it is easier to understand what is going on via dead
simple, dummy examples.  So, let's say we have the following setup:

```python
def get_user_input():
    input = {}
    while True:
        try:
            key, value = raw_input('<key>,<value> or <return>: ').split(',')
            input[key] = value
        except ValueError:
            break
    return process_input(input)

def process_input(input):
    cleaned = {}
    for key, value in input.items():
        cleaned[clean_value(key)] = clean_value(value)
    return cleaned

def clean_value(value):
    return value.strip()
```

If we want to make this safer, and the components more reusable and available
for other components, the main approach would be hardening each component by
introducing error handling, like so:

```python
def get_user_input():
    input = {}
    while True:
        try:
            key, value = raw_input('<key>,<value> or <return>: ').split(',')
            input[key] = value
        except ValueError:
            break
    # If something went wrong processing inputs
    try:
        return process_input(input)
    except TypeError:
        return {}

def process_input(input):
    cleaned = {}
    # If input is not a dict-like object
    try:
        for key, value in input.items():
            try:
                cleaned[clean_value(key)] = clean_value(value)
            except TypeError:
                continue
    except AttributeError:
        raise TypeError('Invalid input type')
    return cleaned

def clean_value(value):
    # If value is not an str-like object
    try:
        return value.strip()
    except AttributeError:
        raise TypeError('Invalid value type')
```

Now, this approach have two downsides.  On one hand, the code is now cluttered,
because all the error checkings are spread across the function, makes it harder
to understand what is the exact problem the function is trying to solve.  On the
other hand the introduced error handling mechanism causes unnecessary overhead,
that is, the checks are running regardless the correctness of the input data.
This is where contract programming comes in.  If we can make sure, that the
top-level component that is using the two other components can guarentee the
correctness of the inputs, it is not necessary to introduce the error handling:

```python
from pcd import contract

@contract(post=lambda r: isinstance(r, dict))
def get_user_input():
    input = {}
    while True:
        try:
            key, value = raw_input('<key>,<value> or <return>: ').split(',')
            input[key] = value
        except ValueError:
            break
    return process_input(input)

@contract(pre=lambda: isinstance(input, dict),
          post=lambda r: isinstance(r, dict))
def process_input(input):
    cleaned = {}
    for key, value in input.items():
        cleaned[clean_value(key)] = clean_value(value)
    return cleaned

@contract(pre=lambda: isinstance(value, str) or
                      isinstance(value, unicode))
def clean_value(value):
    return value.strip()
```

The result is cleaner, easier to read and best of all things, it is
conditionally there and can be removed without touching the code again.  So,
after heavily testing the program with the contracts enabled, the program can be
optimised by stripping the decorators out.

> **Note:** `pcd` currently only supports pre- and postconditions, but later on
> it will introduce *invariants* as well.

> For further info on contract programming, read this [Wikipedia][1] article.

Install
-------

```bash
pip install pcd
```

After the package has been installed import and use it:

```
from pcd import contract
```

For development, clone the [git repository][2] and install the requirements:

```bash
pip install -r requirements.txt
```

To run the tests use `pytest`:

```bash
pytest tests.py
```


Documentation
-------------

The `pcd` module defines the following functions:

<pre><code><b>contract</b><i>(</i><b>pre</b>=[<i>callable</i> or <i>iterable of callables</i>],
         <b>post</b>=[<i>callable</i> or <i>iterable of callables</i>],
         <b>mut</b>=[<i>callable</i> or <i>iterable of callables</i>]<i>)</i></code></pre>

The `pre` should contain all the *preconditions* of the decorated function.
Each *callable* takes no arguments, and can use the same argument names that are
defined by the decorated functions.  Every *callable* sees all the arguments.

The `post` should contain all the *postconditions* of the decorated function.
Each *callable* takes one argument that can be freely named.  This argument will
contain the value the decorated functin is returning.  Every *callable* sees all
the decorated functions's arguments as well.

The `mut` should contain all the *postconditions* of the mutable arguments.
This is very useful if the function has side effects via its arguments.  Each
*callable* takes no arguments, and can use the same argument names that are
defined by the decorated functions.  Every *callable* sees all the arguments.

If `__debug__` is `True` then `contract` has no effect.

- - -

Running the program in a *regular* fashion causes the `contract` to kick in.  To
remove the checks, run the program with optimisations:

```bash
$ python -O sample.py
```


Performance
-----------

Invoking a function with or without the `contract` decorator by running python
with the `-O` (optimisation) flag has asbolutely no performance penalty. The
examples in the `perf.py` shows that both functions have the same amount
instructions and the amount of time to execute them are the same.

Running these functions with the assertions are of course slower than any other
execution due to the argument handling and injection that is done by `contract`.


Testing
-------

Contract programming plays nicely with unit testing.  As a matter of fact it is
highly recommended to test the contracts as one would do with the components
anyway:

```python
from pcd import contract
from pytest import raises

@contract(pre=lambda: len(name) > 0)
def store_name(name):
    pass

if __debug__:
    def test_store_name():
        with raises(AssertionError):
            store_name('')
```


License
-------

Copyright &copy; 2017 Peter Varo hello@petervaro.com

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see http://www.gnu.org/licenses

[0]: img/logo.png?raw=true "pcd"
[1]: https://en.wikipedia.org/wiki/Design_by_contract
[2]: ...