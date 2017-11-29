[![pipeline status][4]][5]

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

Contract programming can boost performance, increase self-documentation coverage
and all in all is a useful code *hardening* technique.  The main principle is
that all components in a program should *agree* on how they are interacting with
each other.  Therefore instead of having isolated components which all have to
guarantee their own correctness, with contract programming entire blocks of
components guarantee their correctness as a unit.

Though Python is not supporting contracts natively as a language feature, there
are several libraries out there trying to add the same functionality to Python.
Sadly they are either broken, or incomplete, or extremely heavy, or simply just
reinventing the wheel by introducing foreign syntax to Python.  Fortunately
there is almost always a light and easy way to do things in Python, and that is
exactly what `pcd` is offering.

Anyway, enough of the abstract *mumbo-jumbo*, let's start talking about how it
works, shall we?  As usual, it is easier to understand what is going on via dead
simple and dummy examples.

So, let's say we have the following setup:

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

If we want to make this safer, and the components more reusable for other
components, the main approach would be hardening each component by introducing
error handling in each function, like so:

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

Now, this approach has two downsides.  On one hand, the code is now cluttered,
because all the error checkings are spread across the functions, making it
harder to understand what the exact problems each of the functions are
trying to solve.  On the other hand the introduced error handling mechanism
causes unnecessary overhead (and sometimes even redundant checkings in seemingly
unrelated places), that is, the checks are running regardless of the correctness
of the input data which may already have been checked.

This is where contract programming comes in!  If we can make sure, that the
top-level component which is using the other two components can guarentee the
correctness of the inputs, it is completely unnecessary to introduce the above
shown error handling:

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

The result is much cleaner, easier to read and understand, and best of all at
the same time it is also conditionally there, and can be removed without
touching the code again.  So, after heavily testing the program with the
contracts enabled, the application can be optimised greatly by stripping the
decorators out.  During the development phase, if another component wants to use
an already *contracted* one then that component has to respect its contracts,
which is exactly what the decorator ensures.

But that's not all!  Contract programming can be used with *classes*.  As a
matter of fact, it can be used very efficiently to take care of data integrity,
which is one of the most important aspects of using user defined types.  Of
course one can use the above explained contracts on selected methods of a class,
but `pcd` offers an even better by implementing *invariants*.

By using invariants, one is automatically generating contracts that are called
after the `__init__`, before the `__del__`, and before and after every public
method and every `property` of a class.  They are inherited by subclasses, and
they can be combined with manually defined contracts as well.

So, let's look at an example:

```python
class Triangle:

    def __init__(self, a, b, c):
        if a <= 0 or b <= 0 or c <=0:
            raise ValueError('All sides need to be greater than 0')
        elif a + b <= c or a + c <= b or b + c <= a:
            raise ValueError(
                'The sum of any two sides has to be greater than the third one')
        self.a = a
        self.b = b
        self.c = c

    @property
    def area(self):
        pass  # Here goes the implementation of Heron's Formula
```

For a seasoned developer it is obvious how dangerious it can be to define (and
then use) *public* side names.  Because eventhough we made sure during the
initialisation, that all sides have valid sizes &mdash; therefore we can safely
call the `area` method on it &mdash; unfortunately we cannot guarantee the data
integrity, as anyone can assign `-1` freely to any of the sides.  Therefore one
is tempted to rewrite the above as follows:

```python
class Triangle:

    def __init__(self, a, b, c):
        self._validate(a, b, c)
        self._a = a
        self._b = b
        self._c = c

    @staticmethod
    def _validate(a, b, c):
        if a <= 0 or b <= 0 or c <=0:
            raise ValueError('All sides need to be greater than 0')
        elif a + b <= c or a + c <= b or b + c <= a:
            raise ValueError(
                'Sum of any two sides have to be greather than the third one')

    @property
    def a(self):
        return self._a
    @a.setter
    def a(self, value):
        self._validate(value, self._b, self._c)
        self._a = value

    @property
    def b(self):
        return self._b
    @b.setter
    def b(self, value):
        self._validate(self._a, value, self._c)
        self._b = value

    @property
    def c(self):
        return self._c
    @a.setter
    def c(self, value):
        self._validate(self._a, self._b, value)
        self._c = value

    @property
    def area(self):
        pass  # Here goes the implementation of Heron's Formula
```

Although this approach is pretty solid (if fellow developers are not overriding
variables marked as private by convention) it is very verbose, and the error
checking is spread across the entire class, not to mention, that it is also
mixed with the logic of the program.  And not only that, but if `Triangle` is
only used internally, that is, the values are not coming from user inputs, but
from a trusted source, the checks are running redundantly anyway, creating quite
an overhead on every assignment.

Let's see how this example would look like with *invariants*:

```python
class Triangle:

    __metaclass__ = Invariant
    __conditions  = (lambda: self.a > 0,
                     lambda: self.b > 0,
                     lambda: self.c > 0,
                     lambda: self.a + self.b > self.c,
                     lambda: self.a + self.c > self.b,
                     lambda: self.b + self.c > self.a)

    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    @property
    def area(self):
        pass  # Here goes the implementation of Heron's Formula
```

All the conditions defined for `Triangle` will run after the call of the
`__init__` method, and before and after the `area` method.  Which means, we can
accidentally override a side to an invalid value, but next time we want to use
that value in a method, it will be checked immediately.  If that is considered
to be too much of a risk, one can also define the getters and setters for each
of the values and the validators will be generated for those as well.  And guess
what?  Yup, the *invariants* can be turned on or off anytime without changing
the code.  And even more!  They are inherited as well!

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
pip install -r requirements_dev.txt
```

To run the tests use `pytest`:

```bash
pytest tests.py
```


Documentation
-------------

The `pcd` module defines the following functions and classes:

<pre><code><b>contract</b><i>(</i><b>pre</b>=[<i>callable</i> or <i>iterable of callables</i>],
         <b>post</b>=[<i>callable</i> or <i>iterable of callables</i>],
         <b>mut</b>=[<i>callable</i> or <i>iterable of callables</i>]<i>)</i></code></pre>

The `pre` should contain all the *preconditions* of the decorated function.
Each *callable* takes no argument, and can use the same argument names that are
defined by the decorated function.  Every *callable* see all arguments.

The `post` should contain all the *postconditions* of the decorated function.
Each *callable* takes one argument which can be named freely.  This argument
will contain the value returned by the decorated function.  Every *callable*
see all of the arguments of the decorated functions as well.

The `mut` should contain all the *postconditions* of the *mutable* arguments.
This can be very useful in case the decorated function has side effects via its
arguments.  Each *callable* takes no argument, and can use the same argument
names that are defined by the decorated function.  The checks are called after
the function returned.  Every *callable* see all arguments.

If `__debug__` is `True` then `contract` has no effect.

- - -

<pre><code><b>Invariant</b><i>()</i></code></pre>

The `Invariant` class can be used as a *metaclass*.  If that is happening, then
the `__conditions` of that class will be automatically executed after the
`__init__` method, before the `__del__` method, and before and after every
public method and `property` invocations.  Each of the conditions can get access
to the `self` variable.

- - -

Running the program in a *regular* fashion causes the `contract` and `Invariant`
to kick in.  To remove the checks, run the program with optimisations:

```bash
$ python -O sample.py
```

- - -

> **WARNING!** One should never change the arguments or the return value of the
> decorated function inside the conditions of the `contract`, as those may be
> mutable values, therefore removing the contracts will alter the behaviour of
> the function and may lead to unexpected behaviour!  The same thing goes for
> the invariant conditions, one shall never mutate anything inside these
> callbacks!


Performance
-----------

Invoking a function with or without the `contract` decorator by running python
with the `-O` (optimisation) flag has asbolutely no performance penalty. The
examples in the `perf.py` shows that both functions have the same amount
of bytecode instructions and their execution times are the same as well.

Running these functions with simple `assert`s instead while `__debug__` is
`True` is course faster than any other execution due to the argument handling
and injection that is done by the `contract` decorator.  However doing so makes
it hard in most cases to check the return value and/or side effects of the
decorated function, and `contract` is a convenient way of doing that.


Testing
-------

Contract programming plays nicely with unit testing.  As a matter of fact it is
highly recommended to test the contracts, and the generic behaviour of the code
component as one would do anyway:

```python
from pcd import contract
from pytest import raises

@contract(pre=lambda: len(name) > 0)
def store_name(name):
    #
    # Normalise and store value ...
    #

    # Return the length of the actual value being stored
    return stored_length

def test_store_name():
    # Check constraints of the contract
    if __debug__:
        with raises(AssertionError):
            store_name('')

    # Check regular behaviour on correct data
    assert srore_name('hello') == 5
```


License
-------

Copyright &copy; 2017 [Peter Varo][3]

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along
with this program.  If not, see http://www.gnu.org/licenses

- - -

Copyright &copy; 2017 [Peter Varo][3]

The logo is licensed under a [Creative Commons Attribution-ShareAlike 4.0
International License][6].

[![license][7]][6]

[0]: img/logo.png?raw=true "pcd"
[1]: https://en.wikipedia.org/wiki/Design_by_contract
[2]: https://gitlab.com/petervaro/pcd
[3]: http://www.petervaro.com
[4]: https://gitlab.com/petervaro/pcd/badges/master/pipeline.svg
[5]: https://gitlab.com/petervaro/pcd/commits/master
[6]: https://creativecommons.org/licenses/by-sa/4.0
[7]: https://i.creativecommons.org/l/by-sa/4.0/80x15.png
