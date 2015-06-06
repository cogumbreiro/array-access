#!/usr/bin/env python
import arith
import ast

def next_index(data, offset=0):
    start = data.index("[", offset)
    if start == -1:
        return ValueError("Could not find start token: [")
    end = data.index("]", start)
    if end == -1:
        return ValueError("Could not find end token: ]")
    next_start = data.index("[", start)
    if next_start != -1 and next_start > end:
        return next_index(data, next_start)
    return (start + 1, end)

DIMS=3

def next_access(data, offset=0, count=DIMS):
    result = []
    for _ in range(count):
        idx1, idx2 = next_index(data, offset)
        result.append((idx1, idx2))
        offset = idx2
    return result

import arith

def parse_index(data):
    #return ast.tojson(arith.eval(data))
    return arith.parse(data)

def parse_subscript_exp(data):
    exps = []
    for (x,y) in next_access(data):
        exps.append(parse_index(data[x:y]))
    return {'env': {"i":1, "j":2, "k":3}, 'indices': exps}

def parse(lines):
    for data in lines:
        try:
            yield parse_subscript_exp(data)
        except ValueError:
            pass

def main(data):
    import json
    import sys
    for x in parse(data):
        json.dump(x, sys.stdout)
        print("")

if __name__ == '__main__':
    import sys
    with open(sys.argv[1]) as fp:
        main(fp.readlines())
