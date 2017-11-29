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
def test_contract():
    raw_input = lambda *a, **k: ''

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

    assert get_user_input() == {}


#------------------------------------------------------------------------------#
def test_invariant():
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

    t = Triangle(3, 4, 5)
    t.a = 9
    raised_with_message(lambda: t.area, 'self.b + self.c > self.a')
