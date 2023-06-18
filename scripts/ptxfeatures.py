#!/usr/bin/env python3
#
# ptxfeatures.py
# Prints a list of PTX features
#
# SPDX-Contributor: Sreepathi Pai
# SPDX-FileCopyrightText: Copyright (C) 2021, University of Rochester
# SPDX-License-Identifier: LGPL-3.0-or-later

import argparse
from ptxparser.ptx_lexer_ply import lexer
from ptxparser.ast2features import PTXAST2Features
import ptxparser as pp
import os

import sys
import time
import json

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Parse a PTX file and print out a list of (AST) features it uses")
    p.add_argument("ptx", help="PTX file")
    p.add_argument("-d", dest="debug", action="store_true", help="Produce parse debug information")
    p.add_argument("-t", dest="tracking", action="store_true", help="Track position")
    p.add_argument("-n", dest="lines", type=int, help="Parse the first N lines", default=1)
    p.add_argument("-a", dest="ast", help="Show AST", action="store_true")
    p.add_argument("-o", dest="output", metavar="FILE", help="Write features to FILE")

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

        print("starting",file=sys.stderr)
        result = pp.ptx_parse(data, debug=args.debug, parse_unsupported=True)

        if result is None:
            print(f"Parser failed",file=sys.stderr)
            sys.exit(1)

        if args.ast and result:
            print(result)

        v = PTXAST2Features()
        v.visit(result)

        out = []
        out.append({'src': os.path.abspath(args.ptx),
                    'features': sorted(v.features)})

        if args.output is None:
            f = sys.stdout
        else:
            f = open(args.output, "w")

        json.dump(out, fp=f, indent=2)
        f.close()

