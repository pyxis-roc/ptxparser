#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021,2023 University of Rochester
#
# SPDX-License-Identifier: LGPL-3.0-or-later
#
# SPDX-Contributor: Sreepathi Pai

from ebnftools.convert import ply as cvtply
from ebnftools.convert import tokens
from ebnftools.ebnfast import EBNFParser
from ebnftools.ebnfanno import parse_annotated_grammar
import argparse
from pathlib import Path
import nametokens
import sys

t_error = """
def t_error(t):
    print(f"ERROR:{t.lineno}: Unexpected character '{t.value[0]}'.", file=sys.stderr)
    INPUT = lexer.lexdata
    sol = INPUT.rfind('\\n', 0, t.lexpos - 1) + 1  # ignore the \\n found
    eol = INPUT.find('\\n', t.lexpos)
    if eol == -1: eol = len(INPUT)
    line = INPUT[sol:eol] # don't include \\n

    print("    " + line, file=sys.stderr)

    # TODO: handle tabs in line correctly when positioning arrow
    if False:
        arrow = "----^"
    else:
        arrow = "\\u25b2"

    print("    " + " "*(t.lexpos-sol-len(arrow)+1)+arrow, file=sys.stderr)
"""

p_error = """
def p_error(p):
    if p is None:
        print("ERROR: Unexpected EOF when parsing", file=sys.stderr)
    else:
        print(f"ERROR:{p.lineno}: Unexpected token '{p.value}' ({p.type}).", file=sys.stderr)
        INPUT = lexer.lexdata
        sol = INPUT.rfind('\\n', 0, p.lexpos - 1) + 1  # ignore the \\n found
        eol = INPUT.find('\\n', p.lexpos)
        if eol == -1: eol = len(INPUT)
        line = INPUT[sol:eol] # don't include \\n

        print("    " + line, file=sys.stderr)

        if False:
            arrow = "----^"
        else:
            arrow = "\\u25b2"

        print("    " + " "*(p.lexpos-sol-len(arrow)+1)+arrow, file=sys.stderr)
"""

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Generate a PLY-based parser for the PTX grammar")
    p.add_argument("bnfgrammar")
    p.add_argument("tokens")
    p.add_argument("-d", dest="output_dir", help="Output directory", default = ".")

    sys.setrecursionlimit(6500)

    args = p.parse_args()

    treg = tokens.TokenRegistry(args.tokens)
    treg.read()

    action_tokens = {"HEX_LITERAL": "Hexadecimal",
                     "OCT_LITERAL": "Octal",
                     "BIN_LITERAL": "Binary",
                     "DEC_LITERAL": "Decimal",
                     "DBL_LITERAL1": "Double",
                     "DBL_LITERAL2": "Double",
                     "DBL_LITERAL3": "Double",
                     "FLTX_LITERAL": "BinFloat",
                     "DBLX_LITERAL": "BinDouble",
                     "ID": "Iden",
                     "SECTION_NAME": "Iden", # SECTION_NAME /\.([a-zA-Z][a-zA-Z0-9_$]*)|([_$%][A-Za-z0-9_$]+)/

    }

    lx = cvtply.LexerGen(treg,  action_tokens = action_tokens, lexermod='ptxtokens', modpath='.')
    lx.t_error = t_error

    for t in nametokens.PTX_65_KEYWORDS:
        tu = "'" + t + "'"
        if tu in treg.v2n:
            lx.add_indirect(t.upper(), 'ID')

    lx.add_ignore('SPACE')

    od = Path(args.output_dir)
    with open(od / "ptx_lexer_ply.py", "w") as f:
        print(lx.get_lexer(), file=f)


    # with open(args.annogrammar, "r") as f:
    #     _, anno = parse_annotated_grammar(f.read())

    # ast_anno = [a for a in anno if a.value[0].value == 'AST']

    # print(ast_anno)

    with open(args.bnfgrammar, "r") as f:
        grs, _ = parse_annotated_grammar(f.read())
        gr = EBNFParser().parse('\n'.join(grs))

    ag = cvtply.CTActionGen(abstract=True)
    prs = cvtply.ParserGen(treg, gr, 'start', actiongen=ag, handlermod='ppactions', modpath='.')
    prs.p_error = p_error

    with open(od / "ptx_parser_ply.py", "w") as f:
        print(prs.get_parser(lexer='.ptx_lexer_ply'), file=f)

    with open(od / "ptxgenactions.py", "w") as f:
        print(prs.get_action_module(), file=f)

