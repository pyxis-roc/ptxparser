TARGET = build

all: $(TARGET)/ptx_grammar.bnf $(TARGET)/ptx_lexer_ply.py $(TARGET)/ptxast.py $(TARGET)/ppactions.py $(TARGET)/ptxtokens.py $(TARGET)/testparser.py $(TARGET)/ptx_grammar.txt

$(TARGET)/ptx_grammar.txt: ptx65_opcodes.txt ptx_expressions.txt
	./gen_ptx_grammar.py $^ $@

$(TARGET)/ptxtokens.py: ptxtokens.py
	cp $< $@

$(TARGET)/testparser.py: testparser.py
	cp $< $@

$(TARGET)/ptxast.py: _ptx_ast.cfg _ast_gen.py _build_ast.py
	python3 _build_ast.py _ptx_ast.cfg $@

$(TARGET)/ppactions.py: ppactions.py
	cp $< $@

$(TARGET)/ptx_grammar.bnf: $(TARGET)/ptx_grammar.txt ptx_tokens.txt
	../ebnftools/ebnftools/cvt2bnf.py $^ > $@
	./nametokens.py ptx_tokens.txt
	../ebnftools/ebnftools/cvt2bnf.py $^ > $@ # to have the names take effect

#$(TARGET)/ptx_expressions.bnf: ptx_expressions.txt ptx_tokens.txt
#	../ebnftools/ebnftools/cvt2bnf.py $^ > $@

$(TARGET)/ptx_lexer_ply.py: $(TARGET)/ptx_grammar.bnf ptx_tokens.txt ptxtokens.py
	./genply.py $< ptx_tokens.txt -d $(TARGET)
