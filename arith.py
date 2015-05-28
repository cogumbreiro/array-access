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

Operand = lambda x: ast.create_atom(parse_constant(x))

def Add(args):
    lhs, _, rhs = args.pop()
    return ast.create_add(lhs, rhs)

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
        [#(signop, 1, opAssoc.RIGHT, EvalSignOp),
         #(multop, 2, opAssoc.LEFT, EvalMultOp),
         (plusop, 2, opAssoc.LEFT, Add),
         #(comparisonop, 2, opAssoc.LEFT, EvalComparisonOp),
         ])

    def parse(self, expr):
        return self.arith_expr.parseString(expr, parseAll=True)[0]


def parse(data):
    """
    >>> parse("i")
    Atom(level=1, const=1, has_var=False)
    >>> parse("1")
    Atom(level=0, const=1, has_var=False)
    >>> parse("i + 1")
    Add(Atom(level=0, const=1, has_var=False), Atom(level=1, const=1, has_var=False))
    """
    try:
        return Arith().parse(data)
    except ParseException:
        raise ValueError

def eval(data):
    """
    >>> eval("1 + 2")
    Atom(level=0, const=3, has_var=False)
    """
    return ast.eval_expr(parse(data))

if __name__ == "__main__":
    import doctest
    doctest.testmod()

#if __name__ == '__main__':
#    import sys
#    expr = sys.argv[1]
#    print repr(expr)
#    print dir(parse(expr).pop())
