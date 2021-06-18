#
# _build_ast.py
#
# Builds the ptx_ast file
#
# Sreepathi Pai

if __name__ == "__main__":
    import argparse
    from _ast_gen import ASTCodeGenerator

    p = argparse.ArgumentParser(description="Generate AST classes for PTX")
    p.add_argument("cfg", nargs="?", help="CFG file", default="_ptx_ast.cfg")
    p.add_argument("output", nargs="?", help="Output file", default="ptx_ast.py")
    args = p.parse_args()

    ast_gen = ASTCodeGenerator(args.cfg)
    ast_gen.generate(open(args.output, 'w'))
