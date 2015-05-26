#
# simpleArith.py
#
# Example of defining an arithmetic expression parser using
# the operatorGrammar helper method in pyparsing.
#
# Copyright 2006, by Paul McGuire
#

from pyparsing import *

integer = Word(nums).setParseAction(lambda t:int(t[0]))
variable = Word(alphas,exact=1)
operand = integer | variable

signop = oneOf('+ -')
multop = oneOf('* /')
plusop = oneOf('+ -')

OP = {
    '+': lambda x, y: x + y,
    '-': lambda x, y: x - y,
    '*': lambda x, y: x * y,
    '/': lambda x, y: x / y
}

Expr = operatorPrecedence( operand,
    [(signop, 1, opAssoc.RIGHT),
     (multop, 2, opAssoc.LEFT),
     (plusop, 2, opAssoc.LEFT),]
    )

def normalize(expr):
    if type(expr) != ParseResults:
        return expr
    lhs, op, rhs = expr

    if type(lhs) == type(rhs) and type(lhs) != str:
        return OP[op](lhs, rhs)

    return (lhs, op, rhs)

def parse_aux(expr, dims=("i", "j", "k")):
    """
    >>> one = parse_aux(1)
    >>> one == {'constant': 1, 'variable': False}
    True
    >>> i = parse_aux("i")
    >>> i == {'constant': 1, 'variable': False, 'name': 'i'}
    True
    >>> i_plus_1 = parse_aux(("i", "+", 1))
    >>> i_plus_1 == {'constant': one, 'variable': i}
    True
    >>> parse_aux(("i", "*", 1)) == {'constant': 1, 'variable': False, 'name': 'i'}
    True
    >>> minus_one = dict(one)
    >>> minus_one['constant'] = -1
    >>> parse_aux(("i", "-", 1)) == {'constant': minus_one, 'variable': i}
    True
    """
    if type(expr) != tuple:
        if expr in dims:
            return {"constant": 1, "variable": False, "name": expr}
        if type(expr) == str:
            return {"constant": 0, "variable": True}

        return {"constant": expr, "variable": False}

    lhs, op, rhs = expr
    lhs = parse_aux(lhs, dims)
    rhs = parse_aux(rhs, dims)
    if op in "-/+":
        if op == '-' and "name" not in rhs:
            rhs['constant'] *= -1
        if "name" in rhs:
            return (rhs, lhs)
        return (lhs, "constant")
    if "name" in lhs:
        if "name" in rhs:
            rhs['variable'] = True
            return rhs
        # rhs is a constant
        tmp = rhs
        rhs = lhs
        lhs = tmp

    # else "name" in rhs:
    rhs['constant'] = lhs['constant'] * rhs['constant']
    rhs['variable'] |= lhs['variable']
    return rhs

def zero():
    return {'constant': 0, 'variable': False}

def fix_parse_aux(data, dims=("i", "j", "k")):
    result = []
    for i in range(len(dims) + 1):
        result.append(zero())

    if type(data) == tuple:
        var, cnst = data
        result[0] = cnst
        data = var
    idx = 1 + dims.index(data['name'])
    del data['name']
    result[idx] = data
    return result


def parse(data):
    """
    >>> x = parse("i")
    >>> len(x)
    4
    >>> x[0] == {'constant': 0, 'variable': False}
    True
    >>> x[1] == {'constant': 1, 'variable': False}
    True
    >>> x[2] == x[1]
    True
    >>> x[3] == x[1]
    True
    """
    expr = normalize(Expr.parseString(data).pop())
    VARS = ("i", "j", "k")
    return fix_parse_aux(parse_aux(data, VARS))

if __name__ == "__main__":
    import doctest
    doctest.testmod()

#if __name__ == '__main__':
#    import sys
#    expr = sys.argv[1]
#    print repr(expr)
#    print dir(parse(expr).pop())
