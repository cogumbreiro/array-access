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
    return ast.tojson(arith.eval(data))

def parse_access(data):
    exps = []
    for (x,y) in next_access(data):
        exps.append(parse_index(data[x:y]))
    return {'type': 'access', 'subscripts': exps}

def parse(lines):
    for data in lines:
        try:
            yield parse_access(data)
        except ValueError:
            pass

def main(data):
    import json
    import sys
    json.dump(list(parse(data)), sys.stdout)

if __name__ == '__main__':
    import sys
    with open(sys.argv[1]) as fp:
        main(fp.readlines())
