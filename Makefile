TARGET = build

all: $(TARGET)/ptx_expressions.bnf $(TARGET)/ptx_lexer_ply.py

$(TARGET)/ptx_expressions.bnf: ptx_expressions.txt
	../ebnftools/ebnftools/cvt2bnf.py $< ptx_tokens.txt > $@

$(TARGET)/ptx_lexer_ply.py: $(TARGET)/ptx_expressions.bnf
	./genply.py $< ptx_tokens.txt -d $(TARGET)
