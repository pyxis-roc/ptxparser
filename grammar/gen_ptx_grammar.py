#!/usr/bin/env python3
#
# gen_ptx_grammar.py
#
# Combines the instruction-testcase generating grammar and the PTX
# file grammar.
#
# Author: Sreepathi Pai

import argparse
from ebnftools.ebnfanno import parse_annotated_grammar
from ebnftools.ebnfconstrain import handle_constraints
from ebnftools.ebnfgen import generate2, flatten
from ebnftools import ebnfast
import itertools
import sys

# didn't seem to help much
# precedence = (
#     ('right', 'TOKEN_Q', 'TOKEN_COLON'),
#     ('left', 'TOKEN_LOR'),
#     ('left', 'TOKEN_LAND'),
#     ('left', 'TOKEN_OR'),
#     ('left', 'TOKEN_CARET'),
#     ('left', 'TOKEN_AND'),
#     ('left', 'TOKEN_EQ', 'TOKEN_NE'),
#     ('left', 'TOKEN_LT', 'TOKEN_GT', 'TOKEN_LE', 'TOKEN_GE'),
#     ('left', 'TOKEN_LSHIFT', 'TOKEN_RSHIFT'),
#     ('left', 'TOKEN_PLUS', 'TOKEN_MINUS'),
#     ('left', 'TOKEN_MUL', 'TOKEN_DIV', 'TOKEN_PERC'),
#     ('right', 'TOKEN_S64', 'TOKEN_U64'),
#     ('right', 'TOKEN_BANG', 'TOKEN_TILD'), # UMINUS and UPLUS were on the rule
#     )


EXPAND_OPCODES = set(['tex_opcode_1', 'tex_opcode_2', 'tex_opcode_3', 'tex_opcode_4', 'tld4_opcode', 'cvt_opcode', 'set_opcode', 'f_add_opcode', 'f_sub_opcode', 'f_mul_opcode', 'fma_opcode', 'setp_opcode',
                      'f_rcp_opcode',# shift/reduce conflict with f_rcp_f64
                      'slct_opcode' # with itself
                      #'wmma_load_opcode', # with itself [leads to a lot more shift/reduce conflicts?'
])

# these opcodes usually generate duplicate opcodes because they were used to generate test cases
DELETE_OPCODES = set(['mov_pack_unpack_opcode', 'mov_pack_unpack_4_opcode',
                      'call_opcode', # has a more complex encoding as call_stmt in ptx_expressions
                      'predicate_opcode' # handled using a separate rule
])

# append rules given in the list to the rule in the key
COMBINE_OPCODES = {'f_add_opcode': ['half_add_opcode'],
                   'f_sub_opcode': ['half_sub_opcode'],
                   'f_mul_opcode': ['half_mul_opcode'],
                   'fma_opcode': ['half_fma_opcode'],
                   'set_opcode': ['half_set_opcode'],
                   'setp_opcode': ['half_setp_opcode']
                   }

# these opcodes are not added to 'opcodes', but shouldn't be deleted either
IGNORE_OPCODES = set(['vmad_opcode'])

def read_constrained_grammar(gfile):
    with open(gfile, "r") as f:
        gd = f.read()

    ebnf, anno = parse_annotated_grammar(gd)
    gr, cgr = handle_constraints(ebnf, anno)

    for x in anno:
        if x.value[0].value != "CONSTRAINT":
            print("WARNING: Unhandled {x} annotation present")

    return cgr

def drop_testcase_rules(gr):
    out = []
    for r in gr:
        if r.lhs.value.endswith('_testcase'): continue
        if r.lhs.value.endswith('_params'): continue
        out.append(r)

    return out

def fold(l, f):
    if len(l) == 1:
        return l[0]
    else:
        return f(l[0], fold(l[1:], f))

def make_alt_rules(rname, lalt):
    # sort by reverse length
    lalt.sort(key=lambda x: x[0])

    nentries = len(lalt)

    if len(lalt) > 300:
        out = []
        for suffix, i in enumerate(range(0, nentries, 300)):
            portion = lalt[i:i+300]
            out.append(("part_" + rname + "_%d" % (suffix,),
                        fold([x[1] for x in portion], ebnfast.Alternation)))

        out.append((rname, fold([ebnfast.Symbol(x[0]) for x in out], ebnfast.Alternation)))
        return out
    else:
        lalt = fold([x[1] for x in lalt], ebnfast.Alternation)
        return [(rname, lalt)]

def gen_sel_mask(grd):
    sel = set()

    sel = set()

    for o in ['vop_sel', 'vop2_sel', 'vop2_mask', 'vop4_mask']:
        newr = []
        for x in generate2(grd, grd[o]):
            xf = ''.join([xx for xx in flatten(x) if xx != ''])

            sel.add(xf)

    sel.remove('')
    assert 'sel_op' not in grd
    return [ebnfast.Rule(ebnfast.Symbol('SEL_OP4'), ebnfast.String('__external__')),
            ebnfast.Rule(ebnfast.Symbol('sel_op'),
                        ebnfast.Alternation(ebnfast.Symbol('SEL_OP4'),
                                            fold([ebnfast.String(x) for x in sel],
                                                 ebnfast.Alternation)))]


def expand_opcodes(gr, opcodes, delete_opcodes, combine_opcodes):
    opcodes = set(opcodes)
    grd = dict([(r.lhs.value, r.rhs) for r in gr])

    sel_op = gen_sel_mask(grd)

    combined_opcodes = set()
    for k in combine_opcodes:
        assert k in grd, f"ERROR: Rule {k} does not exist"

        tmp = []
        for x in combine_opcodes[k]:
            assert x in grd, f"ERROR: Rule {x} does not exist"
            tmp.append(grd[x])
            combined_opcodes.add(x)

        tmp = fold(tmp, ebnfast.Alternation)
        grd[k] = ebnfast.Alternation(grd[k], tmp)

    parts = {}
    for o in opcodes:
        if o not in grd: continue

        newr = []
        dups = set()
        for x in generate2(grd, grd[o]):
            xf = tuple([xx for xx in flatten(x) if xx != ''])
            if xf in dups: continue
            dups.add(xf)
            xfr = (len(xf), fold([ebnfast.String(xx) for xx in xf], ebnfast.Sequence))
            newr.append(xfr)

        parts[o] = []
        for r, l in make_alt_rules(o, newr):
            parts[o].append(r)
            grd[r] = l

    out = []
    for r in gr:
        if r.lhs.value in delete_opcodes or r.lhs.value in combined_opcodes:
            continue

        if r.lhs.value in parts:
            for x in parts[r.lhs.value]:
                out.append(ebnfast.Rule(ebnfast.Symbol(x), grd[x]))
        else:
            out.append(ebnfast.Rule(r.lhs, grd[r.lhs.value]))

    out.extend(sel_op)
    return out

def gather_opcodes(gr, opcodes = None):
    if opcodes is None or len(opcodes) == 0:
        out = []
        for r in gr:
            if r.lhs.value.endswith('_opcode') and r.lhs.value not in IGNORE_OPCODES:
                out.append(r.lhs.value)
    else:
        out = opcodes

    gr.append(f"opcodes ::= {' | '.join(out)}")
    return gr

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Generate a PTX grammar")
    p.add_argument("tcgrammar", help="Instruction testcase grammar")
    p.add_argument("remgrammar", help="Remainder of PTX grammar")
    p.add_argument("output", help="Output Combined grammar")
    p.add_argument("-o", dest="opcodes", help="Opcodes, useful for testing", action="append", default=[])
    #sys.setrecursionlimit(10000)

    args = p.parse_args()

    cgr = read_constrained_grammar(args.tcgrammar)
    remgr = read_constrained_grammar(args.remgrammar)

    # could stream instead of multipass ...
    gr_without_tc = drop_testcase_rules(cgr)
    gr_expanded = expand_opcodes(gr_without_tc, EXPAND_OPCODES, DELETE_OPCODES, COMBINE_OPCODES)
    gr_opcodes = gather_opcodes(gr_expanded, args.opcodes)

    with open(args.output, "w") as f:
        for r in itertools.chain(gr_opcodes, remgr):
            print(str(r), file=f)
