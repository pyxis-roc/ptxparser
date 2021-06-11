#!/usr/bin/env python3

import argparse
from ptx_lexer_ply import lexer
from ptx_parser_ply import parser
import re

# PTX is ASCII
version_dir_re = re.compile(r'\s*.version[ \t]+(?P<major>[0-9])\.(?P<minor>[0-9]+)', re.ASCII)

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Parse a PTX file")
    p.add_argument("ptx", help="PTX file")
    p.add_argument("-d", dest="debug", action="store_true", help="Produce parse debug information")
    p.add_argument("-t", dest="tracking", action="store_true", help="Track position")
    p.add_argument("-n", dest="lines", type=int, help="Parse the first N lines", default=1)
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
        result = parser.parse(data, lexer=lexer, debug=args.debug, tracking=args.tracking)
        print(result)
