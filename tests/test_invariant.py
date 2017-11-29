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

from pcd          import Invariant, contract
from tests.helper import raised_with_message


#------------------------------------------------------------------------------#
def test_simple_init_passes():
    class Class(object):

        __metaclass__ = Invariant
        __conditions  = (lambda: self._property == 'hello',)

        def __init__(self):
            self._property = 'hello'

    Class()


#------------------------------------------------------------------------------#
def test_simple_init_fails():
    class Class(object):

        __metaclass__ = Invariant
        __conditions  = (lambda: self._property == 'hello',)

        def __init__(self):
            self._property = 'world'

    raised_with_message(lambda: Class(), "self._property == 'hello'")


#------------------------------------------------------------------------------#
def test_simple_del_passes():
    class Class(object):

        __metaclass__ = Invariant
        __conditions  = (lambda: self._resource is None,)

        _resource = None

        def __del__(self):
            pass

    Class().__del__()


#------------------------------------------------------------------------------#
def test_simple_del_fails():
    class Class(object):

        __metaclass__ = Invariant
        __conditions  = (lambda: self._resource is None,)

        _resource = NotImplemented

        def __del__(self):
            pass

    raised_with_message(lambda: Class().__del__(), 'self._resource is None')


#------------------------------------------------------------------------------#
def test_simple_method():
    class Class(object):

        __metaclass__ = Invariant
        __conditions  = (lambda: self._alpha is None,
                         lambda: self._beta  is NotImplemented)

        def __init__(self):
            self._alpha = None
            self._beta  = NotImplemented

        def passes(self):
            self._alpha = None
            self._beta  = NotImplemented

        def fails_1(self):
            self._alpha = -9999

        def fails_2(self):
            self._beta = -9999

    Class().passes()
    raised_with_message(lambda: Class().fails_1(), 'self._alpha is None')
    raised_with_message(
        lambda: Class().fails_2(), 'self._beta is NotImplemented')
    c = Class()
    c._alpha = -9999
    raised_with_message(lambda: c.passes(), 'self._alpha is None')


#------------------------------------------------------------------------------#
def test_simple_inheritance():
    class Super(object):

        __metaclass__ = Invariant
        __conditions  = (lambda: self._value == 'value',)

    class Sub(Super):

        def __init__(self):
            self._value = -9999

    raised_with_message(lambda: Sub(), "self._value == 'value'")


#------------------------------------------------------------------------------#
def test_simple_inheritance_extend_invariant():
    class Super(object):

        __metaclass__ = Invariant
        __conditions  = (lambda: self._alpha == 0,)

    class Sub(Super):

        __conditions= (lambda: self._beta == 1,)

        _alpha = 0
        _beta  = 1

        def fails_super(self):
            self._alpha = -9999

        def fails_sub(self):
            self._beta = -9999

    raised_with_message(lambda: Sub().fails_super(), 'self._alpha == 0')
    raised_with_message(lambda: Sub().fails_sub(), 'self._beta == 1')


#------------------------------------------------------------------------------#
def test_complex_inheritance_meta():
    class Meta(Invariant):

        def __new__(self, name, bases, attributes):
            def special_fails(self):
                self._property = -9999
            attributes['special_fails'] = special_fails
            return super(Meta, self).__new__(self, name, bases, attributes)

    class Class(object):

        __metaclass__ = Meta
        __conditions  = (lambda: self._property == 11,)

        _property = 11

    raised_with_message(lambda: Class().special_fails(), 'self._property == 11')


#------------------------------------------------------------------------------#
def test_complex_inheritance_multiple_inheritance_meta():
    class Super1(object):

        __metaclass__ = Invariant
        __conditions  = (lambda: self._number % 2 == 0,)

    class Super2(object):

        __metaclass__ = Invariant
        __conditions  = (lambda: self._number % 3 == 0,)

    class Sub(Super1, Super2):

        __conditions= (lambda: self._number % 5 == 0,)

        def __init__(self, number):
            self._number = number

    raised_with_message(lambda: Sub(15), 'self._number % 2 == 0')
    raised_with_message(lambda: Sub(10), 'self._number % 3 == 0')
    raised_with_message(lambda: Sub(6), 'self._number % 5 == 0')


#------------------------------------------------------------------------------#
def test_with_contract():
    class Class(object):

        __metaclass__ = Invariant
        __conditions  = (lambda: self._property is None,)

        def __init__(self):
            self._property = None

        @contract(pre=lambda: 0 < argument < 9)
        def method(self, argument, property):
            self._property = property

    raised_with_message(
        lambda: Class().method(11, None), '0 < argument < 9')
    raised_with_message(
        lambda: Class().method(5, True), 'self._property is None')
