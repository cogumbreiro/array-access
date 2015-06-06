from pyparsing import *
import ast

def parse_constant(data):
    data = data.pop()
    try:
        return int(data)
    except: pass
    try:
        return float(data)
    except: pass
    return data

#Operand = lambda x: ast.create_atom(parse_constant(x))
Operand = parse_constant

#def Add(args):
#    lhs, _, rhs = args.pop()
#    return ast.create_add(lhs, rhs)

def BinOp(args):
    lhs, op, rhs = args.pop()
    return {'op': op, 'args': [lhs, rhs]}

def UnOp(args):
    op, exp = args.pop()
    return {'op': op, 'args': [exp]}

class Arith:
    # define the parser
    integer = Word(nums)
    real = ( Combine(Word(nums) + Optional("." + Word(nums))
                     + oneOf("E e") + Optional( oneOf('+ -')) + Word(nums))
             | Combine(Word(nums) + "." + Word(nums))
             )

    variable = Word(alphas)
    operand = real | integer | variable

    signop = oneOf('+ -')
    multop = oneOf('* / // %')
    plusop = oneOf('+ -')
    comparisonop = oneOf("< <= > >= == != <>")

    operand.setParseAction(Operand)
    arith_expr = operatorPrecedence(operand,
        [(signop, 1, opAssoc.RIGHT, UnOp),
         (multop, 2, opAssoc.LEFT, BinOp),
         (plusop, 2, opAssoc.LEFT, BinOp),
         #(comparisonop, 2, opAssoc.LEFT, EvalComparisonOp),
         ])

    def parse(self, expr):
        return self.arith_expr.parseString(expr, parseAll=True)[0]


def parse(data):
#    """
#    >>> parse("i")
#    Atom(level=1, const=1, has_var=False)
#    >>> parse("1")
#    Atom(level=0, const=1, has_var=False)
#    >>> parse("i + 1")
#    Add(Atom(level=0, const=1, has_var=False), Atom(level=1, const=1, has_var=False))
#    """
    """
    >>> parse("i")
    'i'
    >>> parse("1")
    1
    >>> parse("i + 1") == {'op': '+', "args": ["i", 1]}
    True
    """
    try:
        return Arith().parse(data)
    except ParseException:
        raise ValueError

def eval(data):
    """
    >>> eval("1 + 2") == {'op': '+', 'args': [1, 2]}
    True
    """
#    """
#    >>> eval("1 + 2")
#    Atom(level=0, const=3, has_var=False)
#    """
    return parse(data)
    # ast.eval_expr(parse(data))

if __name__ == "__main__":
    import doctest
    doctest.testmod()

