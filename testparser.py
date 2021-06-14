#!/usr/bin/env python3

import argparse
from ptx_lexer_ply import lexer
from ptx_parser_ply import parser
import re
import ptxgenactions as pga
import ptxast as pa
from ebnftools.convert.ply import utils
import sys

def _mks(ct):
    return ''.join(utils.dfs_token_list_rec(ct))

class PTXAST2Code(pa.NodeVisitor):
    def __init__(self, outputf):
        self.indent = 0
        self.of = outputf

    def _enter_block(self):
        self.indent += 1

    def _exit_block(self):
        self.indent -= 1
        assert self.indent >= 0

    def _o(self, s, end='\n'):
        print('   '*self.indent + s, end=end, file=self.of)

    def visit_Id(self, node):
        return node.name

    def visit_IntLiteral(self, node):
        x = str(node.value)
        if node.unsigned: x += "U"
        return x

    def visit_BinOp(self, node):
        return f"({self.visit(node.left)}) {node.op} ({self.visit(node.right)})"

    def visit_UnOp(self, node):
        return f"{node.op} ({self.visit(node.expr)})"

    def visit_Ternary(self, node):
        return f"({self.visit(node.cond)}) ? ({self.visit(node.true)}) : ({self.visit(node.false)})"

    def visit_Cast(self, node):
        return f"(({node.cast}) ({self.visit(node.expr)})"

    def visit_ConstExpr(self, node):
        return self.visit(node.expr)

    def visit_ParametricVarname(self, node):
        return f"{node.prefix}<{node.count}>"

    def visit_VectorComp(self, node):
        return f"{self.visit(node.var)}{node.comp}"

    def visit_Label(self, node):
        return f"{node.name}:"

    def visit_VectorOpr(self, node):
        elts = [self.visit(x) for x in node.elts]
        return f"{{{', '.join(elts)}}}"

    def visit_VarInit(self, node):
        var = self.visit(node.var)
        if node.init:
            var = var + f" = {self.visit(node.init_)}"

        return var

    def visit_MultivarDecl(self, node):
        l = []
        l.append(_mks(node.ss))
        if node.align: l.append(f".align {str(node.align)}")
        if node.vector: l.append(node.vector)
        l.append(_mks(node.type))

        x = []
        for p in node.varinit:
            x.append(self.visit(p))

        l.append(', '.join(x))
        self._o(' '.join(l) + ';')

    def visit_Param(self, node):
        out = []
        out.append(node.ss)
        if node.align is not None: out.append(node.align)
        if node.vector is not None: out.append(node.vector)
        out.append(''.join(utils.dfs_token_list_rec(node.type)))
        out.append(self.visit(node.name))
        return ' '.join(out)


    def visit_AddressOpr(self, node):
        out = [self.visit(node.value)]
        if node.offset is not None:
            out.append("+")
            out.append(self.visit(node.offset))

        return f"[{''.join(out)}]"

    def visit_Predicate(self, node):
        return f"@{'!' if node.negate else ''}{self.visit(node.reg)}"

    def visit_ArrayDecl(self, node):
        dim = "".join([f"[{self.visit(v)}]" for v in node.dim])
        return f"{self.visit(node.name)}{dim}"

    def visit_Statement(self, node):
        out = []
        if node.label: out.append(self.visit(node.label))
        if node.predicate: out.append(self.visit(node.predicate))

        out.append("".join(utils.dfs_token_list_rec(node.opcode)))

        sa = []
        for a in node.args:
            sa.append(self.visit(a))
            #else:
            #    sa.append(_mks(a))

        out.append(", ".join(sa))
        self._o(" ".join(out) + ";")

    def visit_Block(self, node):
        self._o("{")
        self._enter_block()
        self.generic_visit(node)
        self._exit_block()
        self._o("}")

    def visit_Entry(self, node):
        l = ['.entry']
        l.append(self.visit(node.name))
        p = "(" + ", ".join([self.visit(p) for p in node.params]) + ")"
        l.append(p)
        self._o(' '.join(l))
        self.visit(node.body)

    def visit_Linker(self, node):
        self._o(node.directive, end=' ')
        self.visit(node.identifier)

    def visit_Target(self, node):
        self._o(f".target {', '.join(node.targets)}")
        if node.address_size:
            self._o(f".address_size {node.address_size}")

    def visit_Module(self, node):
        self._o(f".version {node.version}")
        self.generic_visit(node)

# PTX is ASCII
version_dir_re = re.compile(r'\s*.version[ \t]+(?P<major>[0-9])\.(?P<minor>[0-9]+)', re.ASCII)

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Parse a PTX file")
    p.add_argument("ptx", help="PTX file")
    p.add_argument("-d", dest="debug", action="store_true", help="Produce parse debug information")
    p.add_argument("-t", dest="tracking", action="store_true", help="Track position")
    p.add_argument("-n", dest="lines", type=int, help="Parse the first N lines", default=1)
    p.add_argument("-o", dest="output", help="Parsed and Reconstituted output", default="reparse.ptx")
    args = p.parse_args()

    with open(args.ptx, 'r') as f:
        data = f.read()
        v = version_dir_re.match(data)
        if v is None:
            print("ERROR: No .version directive found\n")
            sys.exit(1)
        print(v.group('major'), v.group('minor'), len(v.group(0)))
        data = data[len(v.group(0)):].split('\n')
        if args.lines == 0: args.lines = len(data)
        data = '\n'.join(data[0:args.lines])
        result = parser.parse(data, lexer=lexer, debug=args.debug, tracking=args.tracking)

        if result is None:
            sys.exit(1)

        result.version = f"{v.group('major')}.{v.group('minor')}"
        #print(result)

        # for x in result:
        #     if isinstance(x, pa.Linker):
        #         if isinstance(x.identifier, pa.Entry):
        #             for s in x.identifier.body:
        #                 if isinstance(s, pa.Statement):
        #                     print(utils.dfs_token_list_rec(s.opcode))

        with open(args.output, "w") as f:
            v = PTXAST2Code(outputf=f)
            v.visit(result)



