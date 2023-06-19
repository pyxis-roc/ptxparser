#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021,2023 University of Rochester
#
# SPDX-License-Identifier: LGPL-3.0-or-later

import argparse
from ptxparser.ptx_lexer_ply import lexer
from ptxparser.ast2ptx import PTXAST2Code
import ptxparser as pp

import sys
import time

def perf(start, end, size):
    total = end - start # fractions of seconds
    size = size / 1048576 # in MiB

    return size / total # MiB/s

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Parse a PTX file")
    p.add_argument("ptx", help="PTX file")
    p.add_argument("-d", dest="debug", action="store_true", help="Produce parse debug information")
    p.add_argument("-t", dest="tracking", action="store_true", help="Track position")
    p.add_argument("-n", dest="lines", type=int, help="Parse the first N lines", default=1)
    p.add_argument("-o", dest="output", help="Parsed and Reconstituted output", default="reparse.ptx")
    p.add_argument("-a", dest="ast", help="Show AST", action="store_true")
    p.add_argument("-l", dest="lex_only", action="store_true", help="Only run lexer")
    args = p.parse_args()

    with open(args.ptx, 'r') as f:
        data = f.read()

        v = pp.ptx_version(data)
        if v is None:
            print("ERROR: No .version directive found\n")
            sys.exit(1)

        print(f"PTX .version is {v[0][0]}.{v[0][1]}")
        if v[0] > pp.PTX_VERSION_MAX:
            print(f"WARNING: Parser only supports upto {pp.PTX_VERSION_MAX[0]}.{pp.PTX_VERSION_MAX[1]}")

        if args.lines > 0:
            args.lines = len(data)
            data = data.split('\n')
            data = '\n'.join(data[0:args.lines])

        print("starting")
        start = time.monotonic()
        if args.lex_only:
            lexer.input(data)
            while lexer.token() is not None: pass
            result = None
        else:
            result = pp.ptx_parse(data, debug=args.debug, parse_unsupported=True)

        end = time.monotonic()

        speed = perf(start, end, len(data))
        print(f"Total time: {(end - start):0.2f}s ({speed:0.2f} MB/s)")

        if result is None:
            print(f"Parser failed")
            sys.exit(1)

        if args.ast and result:
            print(result)

        with open(args.output, "w") as f:
            v = PTXAST2Code(outputf=f)
            v.visit(result)



