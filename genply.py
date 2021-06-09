#!/usr/bin/env python3

from ebnftools.convert import ply as cvtply
from ebnftools.convert import tokens
from ebnftools.ebnfast import EBNFParser
from ebnftools.ebnfanno import parse_annotated_grammar
import argparse
from pathlib import Path

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Generate a PLY-based parser for the PTX grammar")
    p.add_argument("bnfgrammar")
    p.add_argument("tokens")
    p.add_argument("-d", dest="output_dir", help="Output directory", default = ".")

    args = p.parse_args()

    treg = tokens.TokenRegistry(args.tokens)
    treg.read()

    lx = cvtply.LexerGen(treg)

    # for t in nametokens.PTX_65_KEYWORDS:
    #     lx.add_indirect(t.upper(), 'ID')

    #lx.add_ignore('SPACE')

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

    ag = cvtply.CTActionGen()
    prs = cvtply.ParserGen(treg, gr, 'constexpr', actiongen=ag, handlermod='ptxgenactions')

    with open(od / "ptx_parser_ply.py", "w") as f:
        print(prs.get_parser(lexer='ptx_lexer_ply'), file=f)

    with open(od / "ptxgenactions.py", "w") as f:
        print(prs.get_action_module(), file=f)

