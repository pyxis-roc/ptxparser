#!/usr/bin/env python

# SPDX-FileCopyrightText: 2021,2023 University of Rochester
#
# SPDX-License-Identifier: LGPL-3.0-or-later
#
# SPDX-Contributor: Sreepathi Pai

import argparse
from ebnftools.ebnfast import Alternation, String, Sequence, Symbol, Optional
from ebnftools.ebnfanno import parse_annotated_grammar
from ebnftools.ebnfconstrain import handle_constraints
import sys
import re

ALLOWED = set(['.cc', '.approx', '.to'])

def alternations(a):
    while isinstance(a, Alternation):
        yield a.expr[0]
        a = a.expr[1]

    yield a


def get_prefix(r, prefixes):
    def visitor(rx, prefix):
        if isinstance(rx, String):
            if len(prefix) == 0 or (len(prefix) == 1 and rx.value in ALLOWED):
                prefix.append(rx.value)
        elif isinstance(rx, Sequence):
            visitor(rx.expr[0], prefix)
            visitor(rx.expr[1], prefix)
        elif isinstance(rx, (Symbol, Optional)):
            return # turn back on the first symbol
        elif isinstance(rx, Alternation):
            # assume common prefixes
            visitor(rx.expr[0], prefix)
            # not visiting expr[1]
        else:
            raise NotImplementedError(f"{repr(rx)}")

    p = []
    visitor(r, p)
    pfx = ''.join(p)
    assert len(pfx) > 0, f"Found empty prefix for {r}"
    #assert pfx not in prefixes, f"Duplicate prefix {pfx} for {r}"
    prefixes.add(pfx)
    return pfx

def get_prefixes(gr):
    def visit_leaf_symbol(s, prefixes):
        for a in alternations(s):
            # assume rules are either 'prefix1' 'prefix2' ... or opcode_1 | opcode_2

            if isinstance(a, Symbol):
                # opcode_1 | opcode_2
                pfx = visit_leaf_symbol(grd[a.value], prefixes)
            elif isinstance(a, Sequence):
                # 'prefix1' 'prefix2' ...
                if isinstance(a.expr[0], String):
                    pfx = get_prefix(a, prefixes)
                    print(opcode.value, pfx)
                    return pfx
                elif isinstance(a.expr[0], Symbol):
                    pfx = visit_leaf_symbol(grd[a.expr[0].value], prefixes)
                    print(opcode.value, pfx)
                    return pfx
                else:
                    # symbol1 symbol2 symbol3 ...
                    pfx = visit_leaf_symbol(a.expr[0], prefixes)
                    print(opcode.value, pfx)
                    return pfx
            elif isinstance(a, String):
                pfx = a.value
                print(opcode.value, pfx)
                return pfx
            else:
                raise NotImplementedError(f"{repr(a)} not supported")

    grd = dict([(r.lhs.value, r.rhs) for r in gr])

    prefixes = set()
    for opcode in alternations(grd['opcodes']):
        if opcode.value == 'lop3_immLut_opcode': continue # TODO: fix this in the grammar
        print(opcode)
        visit_leaf_symbol(grd[opcode.value], prefixes)

    print(prefixes, len(prefixes))
if __name__ == '__main__':
    p = argparse.ArgumentParser(description="Get instruction prefixes for PTX instructions")
    p.add_argument("grammar", help="Grammar produced by gen_ptx_grammar.py")

    sys.setrecursionlimit(10000)

    args = p.parse_args()

    with open(args.grammar, "r") as f:
        ebnf, anno = parse_annotated_grammar(f.read()) # strange API
        gr, cgr = handle_constraints(ebnf, anno)

    if len(anno):
        print("ERROR: Can't handle annotations")
        sys.exit(1)

    get_prefixes(gr)
