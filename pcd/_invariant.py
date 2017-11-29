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

from inspect       import isfunction
from pcd._contract import contract, prepare_conditions

__all__ = 'Invariant',


# TODO: Consider adding auto-generated __init__ and __del__ methods if those are
#       not present in


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
_CONDITIONS      = '_{}__conditions'
_CONDITION_TYPES = {'pre': 'invariant precondition',
                    'mut': 'invariant postcondition'}
_METHOD_NAME     = '{}.{}'
_DUNDER_METHODS  = {'__repr__', '__str__', '__lt__', '__le__', '__eq__',
                    '__ne__', '__gt__', '__ge__', '__cmp__', '__rcmp__',
                    '__hash__', '__nonzero__', '__unicode__', '__getattr__',
                    '__setattr__', '__delattr__', '__getattribute__', '__get__',
                    '__set__', '__delete__', '__instancecheck__',
                    '__subclasscheck__', '__call__', '__len__', '__getitem__',
                    '__missing__', '__setitem__', '__delitem__', '__iter__',
                    '__reversed__', '__contains__', '__getslice__',
                    '__setslice__', '__delslice__', '__add__', '__sub__',
                    '__mul__', '__floordiv__', '__mod__', '__divmod__',
                    '__pow__', '__lshift__', '__rshift__', '__and__', '__xor__',
                    '__or__', '__div__', '__truediv__', '__radd__', '__rsub__',
                    '__rmul__', '__rdiv__', '__rtruediv__', '__rfloordiv__',
                    '__rmod__', '__rdivmod__', '__rpow__', '__rlshift__',
                    '__rrshift__', '__rand__', '__rxor__', '__ror__',
                    '__iadd__', '__isub__', '__imul__', '__idiv__',
                    '__itruediv__', '__ifloordiv__', '__imod__', '__ipow__',
                    '__ilshift__', '__irshift__', '__iand__', '__ixor__',
                    '__ior__', '__neg__', '__pos__', '__abs__', '__invert__',
                    '__complex__', '__int__', '__long__', '__float__',
                    '__oct__', '__hex__', '__index__', '__coerce__',
                    '__enter__', '__exit__'}


#------------------------------------------------------------------------------#
def _add_conditions(function, function_name, **conditions):
    if function is not None:
        try:
            function_conditions = function.__conditions
            for type, conditions in conditions.items():
                function_conditions[type].update(prepare_conditions(
                    conditions, _CONDITION_TYPES[type], function_name))
        except AttributeError:
            function = contract(**conditions)(function)
        return function


#------------------------------------------------------------------------------#
class Invariant(type):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __new__(self, class_name,
                      base_classes,
                      attributes,
                      *args,
                      **kwargs):
        # Get conditions from the super classes
        conditions = set()
        for class_ in base_classes:
            try:
                conditions.update(
                    getattr(class_, _CONDITIONS.format(class_.__name__)))
            except AttributeError:
                continue

        # Collect conditions from the new class
        conditions_attribute = _CONDITIONS.format(class_name)
        try:
            conditions.update(attributes[conditions_attribute])
        except KeyError:
            pass

        # Add contracts to all public functions
        for name, attribute in attributes.items():
            if name == conditions_attribute:
                continue
            # Test conditions after initialiser
            elif name == '__init__':
                attributes[name] = _add_conditions(
                    attribute, '{}.{}'.format(class_name, name), mut=conditions)
            # Test conditions before finaliser
            elif name == '__del__':
                attributes[name] = _add_conditions(
                    attribute, '{}.{}'.format(class_name, name), pre=conditions)
            # Test conditions before and after magic and public methods
            elif name in _DUNDER_METHODS or not name.startswith('_'):
                if isfunction(attribute):
                    attributes[name] = _add_conditions(
                        attribute,
                        '{}.{}'.format(class_name, name),
                        pre=conditions,
                        mut=conditions)
                elif isinstance(attribute, property):
                    attributes[name] = property(
                        fget=_add_conditions(
                            attribute.fget,
                            '{}.{}: getter'.format(class_name, name),
                            pre=conditions,
                            mut=conditions),
                        fset=_add_conditions(
                            attribute.fset,
                            '{}.{}: setter'.format(class_name, name),
                            pre=conditions,
                            mut=conditions),
                        fdel=_add_conditions(
                            attribute.fdel,
                            '{}.{}: deleter'.format(class_name, name),
                            pre=conditions,
                            mut=conditions))

        # Return new class
        return super(Invariant, self).__new__(
            self, class_name, base_classes, attributes)
