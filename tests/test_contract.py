## INFO ##
## INFO ##
"""
pcd - Python Contract Decorator
-------------------------------
Copyright (C) 2017 Peter Varo <hello@petervaro.com>

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from pcd          import contract
from tests.helper import raised_with_message


#------------------------------------------------------------------------------#
def test_positional_arguments():
    @contract(pre=(lambda: x >= 0,
               lambda: y is not None,
               lambda: isinstance(y, int),
               lambda: z < 10,
               lambda: isinstance(
                z # multiline
                , # closure
                float)))
    def vector(x, y, z):
        pass

    raised_with_message(lambda: vector(-1, 0, 0), 'x >= 0')
    raised_with_message(lambda: vector(0, None, 0), 'y is not None')
    raised_with_message(lambda: vector(0, type, 0), 'isinstance(y, int)')
    raised_with_message(lambda: vector(0, 0, 10), 'z < 10')
    raised_with_message(lambda: vector(0, 0, 9), 'isinstance(z, float)')
    assert vector(0, 0, 0.0) is None


#------------------------------------------------------------------------------#
def test_default_arguments():
    @contract(pre=(lambda: isinstance(left, int) or isinstance(left, float),
               lambda: isinstance(right, int) or isinstance(right, float)))
    def counter(left=0, right=0):
        pass

    assert counter() is None
    assert counter(12) is None
    assert counter(right=99) is None
    assert counter(4, 6) is None
    assert counter(right=7, left=3) is None
    raised_with_message(lambda: counter(None),
                        'isinstance(left, int) or isinstance(left, float)')
    raised_with_message(lambda: counter(right=None),
                        'isinstance(right, int) or isinstance(right, float)')


#------------------------------------------------------------------------------#
def test_variable_arguments():
    @contract(pre=(lambda: isinstance(prefix, str),
               lambda: infix is None or isinstance(infix, str),
               lambda: all(isinstance(c, str) for c in words)))
    def write(prefix, infix=None, *words):
        pass

    assert write(*'hello') is None
    raised_with_message(lambda: write(True), 'isinstance(prefix, str)')
    raised_with_message(lambda: write('', True),
                        'infix is None or isinstance(infix, str)')
    raised_with_message(lambda: write('', None, [1]),
                        'all((isinstance(c, str) for c in words))')


#------------------------------------------------------------------------------#
def test_keyword_arguments():
    @contract(pre=lambda: 'mobile' in others)
    def contact(id, email, **others):
        pass

    assert contact(0, '@', mobile='123456789') is None
    raised_with_message(lambda: contact(email='@', id=99), "'mobile' in others")


#------------------------------------------------------------------------------#
def test_named_function():
    def is_number(result):
        return isinstance(result, int) or isinstance(result, float)

    @contract(post=is_number)
    def add(a, b):
        return a

    assert add(0, 0) == 0
    raised_with_message(lambda: add(None, 0), 'is_number')


#------------------------------------------------------------------------------#
def test_mutated_postcondition():
    @contract(pre=lambda: len(mutable) == 0,
              mut=lambda: len(mutable) == 1)
    def mutator(mutable):
        mutable.append(None)

    assert mutator([]) is None

    class BlackHole(object):

        def __len__(self):
            return 0

        def append(self, *args, **kwargs):
            pass

    raised_with_message(lambda: mutator(BlackHole()), 'len(mutable) == 1')
