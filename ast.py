
def get_level(atom, vars=("i", "j", "k")):
    """
    >>> get_level(2)
    0
    >>> get_level("x")
    0
    >>> get_level("i")
    1
    >>> get_level("j")
    2
    >>> get_level("k")
    3
    """
    if atom in vars:
        return vars.index(atom) + 1
    return 0

class Atom:
    """
    >>> a1 = Atom(level=0, coef=2, has_var=False)
    >>> a1
    Atom(level=0, coef=2, has_var=False)
    >>> a2 = Atom(0, 2, False)
    >>> a1 == a2
    True
    >>> a1.coef = 3
    >>> a1 == a2
    False
    """
    def __init__(self, level, coef, has_var):
        self.level = level
        self.coef = coef
        self.has_var = has_var
    def __eq__(self, other):
        return self.level == other.level and self.coef == other.coef \
                and self.has_var == other.has_var
    def __repr__(self):
        return "Atom(level=%d, coef=%r, has_var=%r)" \
                % (self.level, self.coef, self.has_var)


def create_atom(expr):
    """
    >>> create_atom(1)
    Atom(level=0, coef=1, has_var=False)
    >>> create_atom("x")
    Atom(level=0, coef=0, has_var=True)
    >>> create_atom("i")
    Atom(level=1, coef=1, has_var=False)
    >>> create_atom("j")
    Atom(level=2, coef=1, has_var=False)
    >>> create_atom("k")
    Atom(level=3, coef=1, has_var=False)
    """
    lvl = get_level(expr)
    if lvl == 0:
        if type(expr) == str:
            # variable found
            return Atom(lvl, 0, True)
        else:
            return Atom(lvl, expr, False)
    return Atom(lvl, 1, False)

def flatten_add(exprs):
    result = []
    for expr in exprs:
        if isinstance(expr, Add):
            result.extend(flatten_add(expr.children))
        else:
            result.append(expr)

    result.sort(key=lambda x: x.level)
    return tuple(result)


class Add:
    """
    >>> Add((create_atom("i"), create_atom(2)))
    Add(Atom(level=1, coef=1, has_var=False), Atom(level=0, coef=2, has_var=False))
    >>> Add((create_atom(1), create_atom(1)))
    Add(Atom(level=0, coef=1, has_var=False), Atom(level=0, coef=1, has_var=False))
    """
    def __init__(self, children):
        self.children = children

    def __eq__(self, other):
        return self.children == other.children

    def __repr__(self):
        return "Add%r" % (self.children,)

def create_add(lhs, rhs):
        return Add(flatten_add((lhs, rhs)))


class Mul:
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def __eq__(self, other):
        return self.lhs == other.lhs and self.rhs == other.rhs

    def __repr__(self):
        return "Mul(%r, %r)" % (self.lhs, self.rhs)

def eval_expr(add):
    """
    >>> eval_expr(create_atom(1)) == create_atom(1)
    True
    >>> eval_expr(create_add(create_atom(1), create_atom(1)))
    Atom(level=0, coef=2, has_var=False)
    >>> eval_expr(create_add(create_atom(1), create_atom("x")))
    Atom(level=0, coef=1, has_var=True)
    >>> eval_expr(create_add(create_add(create_atom(1), create_atom("x")), create_atom(2)))
    Atom(level=0, coef=3, has_var=True)
    >>> eval_expr(create_add(create_add(create_atom(1), create_atom("j")), create_atom("i")))
    Add(Atom(level=0, coef=1, has_var=False), Atom(level=1, coef=1, has_var=False), Atom(level=2, coef=1, has_var=False))
    """
    if not isinstance(add, Add):
        return add

    lhs = None
    result = []
    for rhs in add.children:
        if lhs is not None and lhs.level == rhs.level:
            lhs = Atom(level=lhs.level, \
                    coef=lhs.coef + rhs.coef, \
                    has_var=lhs.has_var or rhs.has_var)
        else:
            if lhs is not None:
                result.append(lhs)
            lhs = rhs

    if len(result) > 0 and lhs is not None and result[-1].level != lhs.level:
        result.append(lhs)

    elif len(result) == 0 and lhs is not None:
        result.append(lhs)

    if len(result) == 1:
        return result[0]
    return Add(tuple(result))

if __name__ == "__main__":
    import doctest
    doctest.testmod()
