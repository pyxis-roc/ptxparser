TARGET = build

all: $(TARGET)/ptx_expressions.bnf $(TARGET)/ptx_lexer_ply.py $(TARGET)/ptxast.py $(TARGET)/ppactions.py $(TARGET)/ptxtokens.py

$(TARGET)/ptxtokens.py: ptxtokens.py
	cp $< $@

$(TARGET)/ptxast.py: _ptx_ast.cfg _ast_gen.py _build_ast.py
	python3 _build_ast.py _ptx_ast.cfg $@


$(TARGET)/ppactions.py: ppactions.py
	cp $< $@

$(TARGET)/ptx_expressions.bnf: ptx_expressions.txt ptx_tokens.txt
	../ebnftools/ebnftools/cvt2bnf.py $^ > $@

$(TARGET)/ptx_lexer_ply.py: $(TARGET)/ptx_expressions.bnf ptx_tokens.txt
	./genply.py $< ptx_tokens.txt -d $(TARGET)
