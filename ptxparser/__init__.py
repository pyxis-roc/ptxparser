# SPDX-FileCopyrightText: 2021,2023 University of Rochester
#
# SPDX-License-Identifier: LGPL-3.0-or-later

import re
from .ptx_lexer_ply import lexer
from .ptx_parser_ply import parser

PTX_VERSION_MAX = (6, 5)

# PTX is ASCII
version_dir_re = re.compile(r'\s*.version[ \t]+(?P<major>[0-9])\.(?P<minor>[0-9]+)', re.ASCII)

def ptx_version(data):
    v = version_dir_re.match(data)
    if v:
        return ((int(v.group(1)), int(v.group(2))), len(v.group(0)))
    else:
        return None

def ptx_parse(data, parse_unsupported = False, debug = False):
    v = ptx_version(data)
    if v is None:
        raise SyntaxError("ERROR: No .version directive found\n")

    if v[0] > PTX_VERSION_MAX and not parse_unsupported:
        return None

    # TODO: avoid this splitting of data?
    result = parser.parse(data[v[1]:], lexer=lexer, debug=debug)
    if result is not None:
        result.version = f"{v[0][0]}.{v[0][1]}"

    return result
