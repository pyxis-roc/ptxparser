#!/usr/bin/env python3
#
# nametokens.py
#
# Simple tool to rename EBNF-extracted tokens
#
# SPDX-FileCopyrightText: 2023 2021 University of Rochester
# SPDX-License-Identifier: LPGL-3.0-or-later

from ebnftools.convert import tokens
import argparse

# https://docs.nvidia.com/cuda/parallel-thread-execution/#identifiers
# this can be expressed in the grammar...
PTX_65_KEYWORDS = {
    'abs',
    'div',
    'or',
    'sin',
    'vavrg2',
    'vavrg4',
    'add',
    'ex2',
    'pmevent',
    'slct',
    'vmad',
    'addc',
    'exit',
    'popc',
    'sqrt',
    'vmax',
    'and',
    'fma',
    'prefetch',
    'st',
    'vmax2',
    'vmax4',
    'atom',
    'isspacep',
    'prefetchu',
    'sub',
    'vmin',
    'bar',
    'ld',
    'prmt',
    'subc',
    'vmin2',
    'vmin4',
    'bfe',
    'ldu',
    'rcp',
    'suld',
    'vote',
    'bfi',
    'lg2',
    'red',
    'suq',
    'vset',
    'bfind',
    'mad',
    'rem',
    'sured',
    'vset2',
    'vset4',
    'bra',
    'mad24',
    'ret',
    'sust',
    'vshl',
    'brev',
    'madc',
    'rsqrt',
    'testp',
    'vshr',
    'brkpt',
    'max',
    'sad',
    'tex',
    'vsub',
    'call',
    'membar',
    'selp',
    'tld4',
    'vsub2',
    'vsub4',
    'clz',
    'min',
    'set',
    'trap',
    'xor',
    'cnot',
    'mov',
    'setp',
    'txq',
    'copysign',
    'mul',
    'shf',
    'vabsdiff',
    'cos',
    'mul24',
    'shfl',
    'vabsdiff2',
    'vabsdiff4',
    'cvt',
    'neg',
    'shl',
    'vadd',
    'cvta',
    'not',
    'shr',
    'vadd2',
    'vadd4',
    # not in the list...
    'dp2a',
    'dp4a',
    'fns',
    'brx',
    'activemask',
    'ldmatrix',
    'wmma',
    'match',
    'fence',
    'lop3',
    'istypep',
    'barrier',
    'nanosleep',
    'mma'
}

OTHER_NAMES = {
    ';': 'SEMICOLON'
    }

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Rename tokens in a token registry")
    p.add_argument('tokenreg')
    args = p.parse_args()

    tr = tokens.TokenRegistry(args.tokenreg)
    tr.read()

    for k in PTX_65_KEYWORDS:
        s = tokens.TknLiteral(k)
        sk = s.key()
        if sk in tr.v2n:
            if tr.v2n[sk] != k.upper():
                old = tr.v2n[sk]
                tr.remove(tr.v2n[sk])
                tr.add(k.upper(), s)
                tr.rename(old, k.upper())

    for k in OTHER_NAMES:
        s = tokens.TknLiteral(k)
        sk = s.key()
        if sk in tr.v2n:
            if tr.v2n[sk] != OTHER_NAMES[k]:
                old = tr.v2n[sk]
                tr.remove(tr.v2n[sk])
                tr.add(OTHER_NAMES[k], s)
                tr.rename(old, OTHER_NAMES[k])

    tr.write_ordered()
