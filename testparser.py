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

    def visit_ParametricVarname(self, node):
        return f"{node.prefix}<{node.count}>"

    def visit_VarInit(self, node):

        if isinstance(node.var.args[0], pa.Node):
            var = self.visit(node.var.args[0])
        else:
            var = _mks(node.var)

        if node.init:
            var = var + f" = {self.visit(node.init_)}"

        return var

    def visit_MultivarDecl(self, node):
        self._o(_mks(node.ss), end=' ')
        if node.align: self._o(node.align, end=' ')
        if node.vector: self._o(node.vector, end=' ')
        self._o(_mks(node.type), end=' ')

        x = []
        for p in node.varinit:
            if isinstance(p, pa.Node):
                x.append(self.visit(p))
            else:
                x.append(str(p))

        self._o(', '.join(x), end='')
        self._o(';')

    def visit_Param(self, node):
        out = []
        out.append(node.ss)
        out.append('' if node.align is None else node.align)
        out.append('' if node.vector is None else node.vector)
        out.append(''.join(utils.dfs_token_list_rec(node.type)))
        out.append(''.join(utils.dfs_token_list_rec(node.name)))
        return ' '.join(out)


    def visit_AddressOpr(self, node):
        out = [node.value]
        if node.offset is not None:
            out.append("+")
            out.append(str(node.offset))

        return f"[{''.join(out)}]"

    def visit_Predicate(self, node):
        return "@{'!' if node.negate else ''}{node.reg}"

    def visit_Statement(self, node):
        out = []
        if node.label: out.append(node.label + ":")
        if node.predicate: out.append(self.visit(node.predicate))

        out.append("".join(utils.dfs_token_list_rec(node.opcode)))

        sa = []
        for a in node.args:
            if isinstance(a, str):
                sa.append(a)
            elif isinstance(a, pa.Node):
                sa.append(self.visit(a))
            else:
                sa.append(_mks(a))

        out.append(", ".join(sa))
        self._o(" ".join(out) + ";")

    def visit_Block(self, node):
        self._o("{")
        self._enter_block()
        self.generic_visit(node)
        self._exit_block()
        self._o("}")

    def visit_Entry(self, node):
        self._o('.entry', end=' ')
        self._o(node.name, end = ' ')
        p = "(" + ", ".join([self.visit(p) for p in node.params]) + ")"
        self._o(p)
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
        result.version = f"{v.group('major')}.{v.group('minor')}"
        #print(result)

        # for x in result:
        #     if isinstance(x, pa.Linker):
        #         if isinstance(x.identifier, pa.Entry):
        #             for s in x.identifier.body:
        #                 if isinstance(s, pa.Statement):
        #                     print(utils.dfs_token_list_rec(s.opcode))
        print(result)

        with open("reparse.ptx", "w") as f:
            v = PTXAST2Code(outputf=f)
            v.visit(result)



