from __future__ import print_function
from timeit     import timeit
from dis        import disassemble

setup="""
from pcd import contract

def without_contract(alpha, beta):
    return cmp(alpha, beta)

@contract(pre=(lambda: alpha is not None,
               lambda: beta is not None))
def with_contract(alpha, beta):
    return cmp(alpha, beta)

def asserted(alpha, beta):
    assert alpha is not None
    assert beta is not None
    return cmp(alpha, beta)

def checked(alpha, beta):
    if alpha is None or beta is None:
        raise AssertionError
    return cmp(alpha, beta)
"""

# Measeure times
print('measured without_contract:',
      timeit('without_contract(True, 12)', setup=setup))
print('measured with_contract:',
      timeit('with_contract(True, 12)', setup=setup))
print('measured asserted:',
      timeit('asserted(True, 12)', setup=setup))
print('measured checked:',
      timeit('checked(True, 12)', setup=setup))

# Check instructions
eval(compile(setup, __file__, mode='exec'), globals(), locals())
print('disassembled without_contract:')
disassemble(without_contract.__code__)
print('disassembled with_contract:')
disassemble(with_contract.__code__)
print('disassembled asserted:')
disassemble(asserted.__code__)
print('disassembled checked:')
disassemble(checked.__code__)
