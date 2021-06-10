TARGET = build

all: $(TARGET)/ptx_expressions.bnf $(TARGET)/ptx_lexer_ply.py

$(TARGET)/ptxtokens.py: ptxtokens.py
	cp $< $@

$(TARGET)/ptxast.py: ptxast.py
	cp $< $@

$(TARGET)/ppactions.py: ppactions.py
	cp $< $@

$(TARGET)/ptx_expressions.bnf: ptx_expressions.txt ptx_tokens.txt
	../ebnftools/ebnftools/cvt2bnf.py $^ > $@

$(TARGET)/ptx_lexer_ply.py: $(TARGET)/ptx_expressions.bnf ptx_tokens.txt $(TARGET)/ptxtokens.py $(TARGET)/ppactions.py $(TARGET)/ptxast.py
	./genply.py $< ptx_tokens.txt -d $(TARGET)
