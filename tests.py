from pytest import raises
from pcd import contract

#------------------------------------------------------------------------------#
# Positional arguments
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

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
def test_positional_arguments():
    try:
        vector(-1, 0, 0)
    except AssertionError as error:
        assert str(error).endswith('x >= 0')

    try:
        vector(0, None, 0)
    except AssertionError as error:
        assert str(error).endswith('y is not None')

    try:
        vector(0, NotImplemented, 0)
    except AssertionError as error:
        assert str(error).endswith('isinstance(y, int)')

    try:
        vector(0, 0, 10)
    except AssertionError as error:
        assert str(error).endswith('z < 10')

    try:
        vector(0, 0, 9)
    except AssertionError as error:
        assert str(error).endswith('isinstance(z, float)')

    assert vector(0, 0, 0.0) is None


#------------------------------------------------------------------------------#
# Default arguments
@contract(pre=(lambda: isinstance(left, int) or isinstance(left, float),
               lambda: isinstance(right, int) or isinstance(right, float)))
def counter(left=0, right=0):
    pass

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
def test_default_arguments():
    assert counter() is None
    assert counter(12) is None
    assert counter(right=99) is None
    assert counter(4, 6) is None
    assert counter(right=7, left=3) is None

    try:
        counter(None)
    except AssertionError as error:
        assert str(error).endswith(
            'isinstance(left, int) or isinstance(left, float)')

    try:
        counter(right=None)
    except AssertionError as error:
        assert str(error).endswith(
            'isinstance(right, int) or isinstance(right, float)')


#------------------------------------------------------------------------------#
# Variable arguments
@contract(pre=(lambda: isinstance(prefix, str),
               lambda: infix is None or isinstance(infix, str),
               lambda: all(isinstance(c, str) for c in words)))
def write(prefix, infix=None, *words):
    pass

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
def test_variable_arguments():
    assert write(*'hello') is None

    try:
        write(True)
    except AssertionError as error:
        assert str(error).endswith('isinstance(prefix, str)')

    try:
        write('', True)
    except AssertionError as error:
        assert str(error).endswith(
            'infix is None or isinstance(infix, str)')

    try:
        write('', None, [1])
    except AssertionError as error:
        assert str(error).endswith(
            'all((isinstance(c, str) for c in words))')


#------------------------------------------------------------------------------#
# Keyword arguments
@contract(pre=lambda: 'mobile' in others)
def contact(id, email, **others):
    pass

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
def test_keyword_arguments():
    assert contact(0, '@', mobile='123456789') is None

    try:
        contact(email='@', id=99)
    except AssertionError as error:
        assert str(error).endswith("'mobile' in others")


#------------------------------------------------------------------------------#
# Named functions as validators
def is_number(result):
    return isinstance(result, int) or isinstance(result, float)

@contract(post=is_number)
def add(a, b):
    return a

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
def test_named_function():
    assert add(0, 0) == 0

    try:
        add(None, 0)
    except AssertionError as error:
        assert str(error).endswith('is_number')


#------------------------------------------------------------------------------#
# Mutated postcondition
@contract(pre=lambda: len(mutable) == 0,
          mut=lambda: len(mutable) == 1)
def mutator(mutable):
    mutable.append(None)

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
def test_mutated_postcondition():
    assert mutator([]) is None

    class BlackHole(object):

        def __len__(self):
            return 0

        def append(self, *args, **kwargs):
            pass

    try:
        mutator(BlackHole())
    except AssertionError as error:
        assert str(error).endswith('len(mutable) == 1')
