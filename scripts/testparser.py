#!/usr/bin/env python3

import argparse
from ptxparser.ptx_lexer_ply import lexer
from ptxparser.ptx_parser_ply import parser
from ptxparser.ast2ptx import PTXAST2Code

import re
import sys
import time


def perf(start, end, size):
    total = end - start # fractions of seconds
    size = size / 1048576 # in MiB

    return size / total # MiB/s

# PTX is ASCII
version_dir_re = re.compile(r'\s*.version[ \t]+(?P<major>[0-9])\.(?P<minor>[0-9]+)', re.ASCII)

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
        v = version_dir_re.match(data)
        if v is None:
            print("ERROR: No .version directive found\n")
            sys.exit(1)

        print(v.group('major'), v.group('minor'), len(v.group(0)))
        data = data[len(v.group(0)):].split('\n')
        if args.lines == 0: args.lines = len(data)
        data = '\n'.join(data[0:args.lines])
        print("starting")
        start = time.monotonic()
        if args.lex_only:
            lexer.input(data)
            #print(len(data))
            while lexer.token() is not None: pass
            result = None
        else:
            result = parser.parse(data, lexer=lexer, debug=args.debug, tracking=args.tracking)
        end = time.monotonic()

        speed = perf(start, end, len(data))
        print(f"Total time: {(end - start):0.2f}s ({speed:0.2f} MB/s)")
        if result is None:
            sys.exit(1)

        result.version = f"{v.group('major')}.{v.group('minor')}"
        if args.ast:
            print(result)

        with open(args.output, "w") as f:
            v = PTXAST2Code(outputf=f)
            v.visit(result)



