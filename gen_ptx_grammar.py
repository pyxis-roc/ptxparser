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
import itertools

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

def gather_opcodes(gr):
    out = []
    for r in gr:
        if r.lhs.value.endswith('_opcode'):
            out.append(r.lhs.value)

    gr.append(f"opcodes ::= {' | '.join(out)}")
    return gr

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Generate a PTX grammar")
    p.add_argument("tcgrammar", help="Instruction testcase grammar")
    p.add_argument("remgrammar", help="Remainder of PTX grammar")
    p.add_argument("output", help="Output Combined grammar")

    args = p.parse_args()

    cgr = read_constrained_grammar(args.tcgrammar)
    remgr = read_constrained_grammar(args.remgrammar)

    # could stream instead of multipass ...
    gr_without_tc = drop_testcase_rules(cgr)
    gr_opcodes = gather_opcodes(gr_without_tc)

    with open(args.output, "w") as f:
        for r in itertools.chain(gr_opcodes, remgr):
            print(str(r), file=f)
