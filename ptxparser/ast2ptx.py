# SPDX-FileCopyrightText: 2021,2023 University of Rochester
#
# SPDX-License-Identifier: LGPL-3.0-or-later

from . import ptxtokens
from . import ptxgenactions as pga
from . import ptxast as pa

from ebnftools.convert.ply import utils

def _mks(ct):
    if isinstance(ct, str):
        # we should prohibit string tokens in RHS except for singletons?
        return ct
    else:
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

    def visit_Generic(self, node):
        return f"generic({self.visit(node.name)})"

    def visit_AddrExpr(self, node):
        off = "" if node.offset is None else f"+{self.visit(node.offset)}"
        return f"{self.visit(node.var)}{off}"

    def visit_DblLiteral(self, node):
        return node.value

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

    def visit_VectorOpr(self, node):
        elts = [self.visit(x) for x in node.elts]
        return f"{{{', '.join(elts)}}}"

    def visit_VarInit(self, node):
        var = self.visit(node.var)
        if node.init:
            var = var + f" = {self.visit(node.init)}"

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

    def visit_ArrayLiteral(self, node):
        y = [self.visit(x) for x in node.elts]
        return f"{{ {', '.join(y)} }}"


    def visit_CallTargets(self, node):
        self._o(".calltargets " + ", ".join([self.visit(p) for p in node.labels]) + ";")

    def visit_BranchTargets(self, node):
        self._o(".branchtargets " + ", ".join([self.visit(p) for p in node.labels]) + ";")

    def visit_TexCoordOpr(self, node):
        l = []
        l.append(self.visit(node.texref))
        if node.sampler:
            l.append(self.visit(node.sampler))
        l.append(self.visit(node.texcoord))

        return "[" + ', '.join(l) + "]"

    def visit_SelOpr(self, node):
        n = "-" if node.negate else ""
        return f"{n}{self.visit(node.name)}{node.sel}"

    def visit_BitbucketArg(self, node):
        return "_"

    def visit_NegatedArg(self, node):
        return f"!{self.visit(node.arg)}"

    def visit_PairedArg(self, node):
        return f"{self.visit(node.args[0])}|{self.visit(node.args[1])}"

    def visit_Param(self, node):
        out = []
        out.append(node.ss)
        if node.align: out.append(f".align {str(node.align)}")
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

    def visit_DwarfLabel(self, node):
        o = f"+{self.visit(node.offset)}" if node.offset is not None else ""
        return f"{node.name.value}{o}"

    def visit_DwarfLine(self, node):
        c = ", ".join([hex(d.value) for d in node.contents]) if isinstance(node.contents, list) else self.visit(node.contents)
        self._o(f"{node.dir} {c}")

    def visit_File(self, node):
        ts = f", {node.timestamp_size[0]}, {node.timestamp_size[1]}" if node.timestamp_size else ""
        self._o(f'.file {node.index} {node.name} {ts}')

    def visit_Loc(self, node):
        self._o(f'.loc {node.index} {node.line} {node.col}')

    def visit_SectionDir(self, node):
        self._o(f".section {node.name.value} {{")
        self._enter_block()
        self.generic_visit(node)
        self._exit_block()
        self._o("}")

    def visit_ArrayDecl(self, node):
        dim = "".join([f"[{self.visit(v) if v is not None else ''}]" for v in node.dim])
        return f"{self.visit(node.name)}{dim}"

    def visit_PragmaDir(self, node):
        return f".pragma {', '.join(node.pragma)}"

    def visit_Label(self, node):
        self._o(f"{node.name}:")

    def _visit_args(self, arglist):
        sa = []
        for a in arglist:
            if isinstance(a, pa.Node):
                sa.append(self.visit(a))
            elif isinstance(a, ptxtokens.BinFloat):
                # this needs to be handled better by converting
                # BinFloat to a proper AST node, perhaps a Constexpr
                # with only it.
                sa.append(a.value)
            else:
                raise NotImplementedError(f"Unknown type of argument {a}")
            #else:
            #    sa.append(_mks(a))

        return ", ".join(sa)

    def visit_CallStmt(self, node):
        out = []
        if node.predicate: out.append(self.visit(node.predicate))
        out.append(node.opcode)

        args = []
        if node.ret_params:
            args.append("(" + self._visit_args(node.ret_params)   + ")")

        args.append(self.visit(node.func))

        if node.params:
            args.append("(" + self._visit_args(node.params)   + ")")

        if node.targets:
            args.append(self.visit(node.targets))

        out.append(", ".join(args))

        self._o(" ".join(out) + ";")

    def visit_Statement(self, node):
        out = []
        if node.predicate: out.append(self.visit(node.predicate))
        out.append("".join(utils.dfs_token_list_rec(node.opcode)))
        out.append(self._visit_args(node.args))
        self._o(" ".join(out) + ";")

    def visit_Block(self, node):
        self._o("{")
        self._enter_block()
        self.generic_visit(node)
        self._exit_block()
        self._o("}")

    def visit_Alias(self, node):
        self._o(f'.alias {self.visit(node.falias)}, {self.visit(node.aliasee)};')

    def visit_CallPrototype(self, node):
        l = ['.callprototype']
        if node.ret_params:
            r = "(" + ", ".join([self.visit(p) for p in node.ret_params]) + ")"
            l.append(r)

        l.append("_")

        if node.params:
            p = "(" + ", ".join([self.visit(p) for p in node.params]) + ")"
            l.append(p)

        if node.noreturn:
            l.append('.noreturn')

        self._o(' '.join(l) + ';')

    def visit_Func(self, node):
        l = ['.func']
        if node.ret_params:
            r = "(" + ", ".join([self.visit(p) for p in node.ret_params]) + ")"
            l.append(r)

        l.append(self.visit(node.name))

        if node.params:
            p = "(" + ", ".join([self.visit(p) for p in node.params]) + ")"
            l.append(p)

        if node.noreturn:
            l.append('.noreturn')

        self._o(' '.join(l))
        if node.body:
            self.visit(node.body)
        else:
            self._o(';') #TODO

    def visit_EntryDir(self, node):
        return f"{node.name} {', '.join([self.visit(p) for p in node.args])}"

    def visit_Entry(self, node):
        l = ['.entry']
        l.append(self.visit(node.name))
        if node.params:
            p = "(" + ", ".join([self.visit(p) for p in node.params]) + ")"
            l.append(p)

        if node.directives:
            l.append(' '.join([self.visit(d) for d in node.directives]))

        self._o(' '.join(l))
        if node.body:
            self.visit(node.body)
        else:
            self._o(';')

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
