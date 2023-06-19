# SPDX-FileCopyrightText: 2021,2023 University of Rochester
#
# SPDX-License-Identifier: LGPL-3.0-or-later

GRAMMAR ?= ../grammar/build/ptx_grammar.bnf
TOKENS ?= ../grammar/ptx_tokens.txt
GENPLY ?= ../grammar/genply.py

all: ptx_lexer_ply.py ptx_parser_ply.py ptxast.py

ptx_lexer_ply.py ptx_parser_ply.py &: $(GRAMMAR) $(TOKENS) ptxtokens.py
	$(GENPLY) $(GRAMMAR) $(TOKENS) -d .

ptxast.py: _ptx_ast.cfg _ast_gen.py _build_ast.py
	python3 _build_ast.py _ptx_ast.cfg $@
