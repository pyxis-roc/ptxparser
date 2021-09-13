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

# from Table 3 of the PTX spec
PREDEFINED_IDS = {
    "%clock",
    "%laneid",
    "%lanemask_gt",
    "%clock64",
    "%lanemask_eq",
    "%nctaid",
    "%smid",
    "%ctaid",
    "%lanemask_le",
    "%ntid",
    "%tid",
    "%lanemask_lt",
    "%nsmid",
    "%warpid",
    "%gridid",
    "%lanemask_ge",
    "%nwarpid",
    "WARP_SZ",
    }

class PTXAST2Features(pa.NodeVisitor):
    def __init__(self):
        self.indent = 0
        self.features = set()

    def add_feature(self, feature):
        self.features.add(feature)

    def _enter_block(self):
        self.indent += 1

    def _exit_block(self):
        self.indent -= 1
        assert self.indent >= 0

    def visit_Id(self, node):
        self.add_feature("Id")
        if node.name in PREDEFINED_IDS:
            self.add_feature(f"Id({node.name})")
        elif node.name.startswith("%pm"):
            # %pm0..7
            self.add_feature("Id(%pm)")
        elif node.name.startswith("%envreg"):
            # envreg<32>
            self.add_feature(f"Id({node.name})")


    def visit_IntLiteral(self, node):
        if node.unsigned:
            self.add_feature("IntLiteral_unsigned")
        else:
            self.add_feature("IntLiteral")

    def visit_Generic(self, node):
        self.visit(node.name)
        self.add_feature("Generic")

    def visit_AddrExpr(self, node):
        if node.offset: self.visit(node.offset)
        self.visit(node.var)

        off = "" if node.offset is None else f"+offset"
        self.add_feature("AddrExpr(offset)")

    def visit_DblLiteral(self, node):
        self.add_feature("DblLiteral")

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)
        self.add_feature(f"BinOp({node.op})")

    def visit_UnOp(self, node):
        self.visit(node.expr)
        self.add_feature(f"UnOp({node.op})")

    def visit_Ternary(self, node):
        self.visit(node.cond)
        self.add_feature("Ternary")
        self.visit(node.true)
        self.visit(node.false)

    def visit_Cast(self, node):
        self.visit(node.expr)
        self.add_feature(node.cast)

    def visit_ConstExpr(self, node):
        self.visit(node.expr)
        self.add_feature("ConstExpr")

    def visit_ParametricVarname(self, node):
        self.add_feature("ParametricVarname")

    def visit_VectorComp(self, node):
        self.visit(node.var)
        self.add_feature(f"VectorComp{node.comp}")

    def visit_VectorOpr(self, node):
        elts = [self.visit(x) for x in node.elts]
        self.add_feature(f"VectorOpr({len(elts)})")

    def visit_VarInit(self, node):
        var = self.visit(node.var)
        if node.init:
            self.visit(node.init)
            self.add_feature("VarInit(init)")
        else:
            self.add_feature("VarInit")

    def visit_MultivarDecl(self, node):
        self.add_feature(f"MultivarDecl(blockdepth={self.indent})")
        self.add_feature(f"MultivarDecl(ss={_mks(node.ss)})")

        if node.align:
            self.add_feature(f"MultivarDecl(align={str(node.align)})")
        else:
            self.add_feature(f"MultivarDecl(align=None)")

        if node.vector:
            self.add_feature(f"MultivarDecl(vector={node.vector})")
        else:
            self.add_feature(f"MultivarDecl(vector=None)")

        self.add_feature(f"MultivarDecl(type={_mks(node.type)})")

        map(self.visit, node.varinit)

    def visit_ArrayLiteral(self, node):
        map(self.visit, node.elts)
        self.add_feature("ArrayLiteral")

    def visit_CallTargets(self, node):
        self.add_feature("CallTargets")

    def visit_BranchTargets(self, node):
        self.add_feature("BranchTargets")

    def visit_TexCoordOpr(self, node):
        # TODO:
        self.add_feature("TexCoordOpr")

        self.visit(node.texref)
        if node.sampler:
            self.add_feature("TexCoordOpr(sampler)")
            self.visit(node.sampler)
        else:
            self.add_feature("TexCoordOpr(nosampler)")

        self.visit(node.texcoord)


    def visit_SelOpr(self, node):
        self.visit(node.name)
        n = "neg" if node.negate else ""
        self.add_feature(f"SelOpr(sel={node.sel},neg={n})")

    def visit_BitbucketArg(self, node):
        self.add_feature("BitbucketArg")

    def visit_NegatedArg(self, node):
        self.add_feature("NegatedArg")

    def visit_PairedArg(self, node):
        self.add_feature("PairedArg")

        self.visit(node.args[0])
        self.visit(node.args[1])

    def visit_Param(self, node):
        out = []
        self.add_feature(f"Param(ss=node.ss)")
        if node.align:
            self.add_feature(f"Param(align={str(node.align)})")
        else:
            self.add_feature(f"Param(align=none)")

        if node.vector is not None:
            self.add_feature(f"Param(vector={node.vector})")
        else:
            self.add_feature(f"Param(vector=none)")

        self.add_feature(f"Param(type={''.join(utils.dfs_token_list_rec(node.type))})")
        self.visit(node.name)

    def visit_AddressOpr(self, node):
        #TODO: how does this differ from AddressExpr?
        self.visit(node.value)
        if node.offset is not None:
            self.add_feature("AddressOpr(offset)")
            self.visit(node.offset)
        else:
            self.add_feature("AddressOpr")

    def visit_Predicate(self, node):
        self.add_feature(f"Predicate{'(negate)' if node.negate else ''}")
        self.visit(node.reg)

    def visit_DwarfLabel(self, node):
        if node.offset is not None:
            self.visit(node.offset)
            self.add_feature("DwarfLabel(offset)")
        else:
            self.add_feature("DwarfLabel")

    def visit_DwarfLine(self, node):
        c = ", ".join([hex(d.value) for d in node.contents]) if isinstance(node.contents, list) else self.visit(node.contents)
        #TODO
        self.add_feature("DwarfLine")

    def visit_File(self, node):
        if node.timestamp_size:
            self.add_feature("File(timestamp_size)")
        else:
            self.add_feature("File")

    def visit_Loc(self, node):
        self.add_feature("Loc")

    def visit_SectionDir(self, node):
        self.add_feature("SectionDir")
        self._enter_block()
        self.generic_visit(node)
        self._exit_block()

    def visit_ArrayDecl(self, node):
        for v in node.dim:
            if v is not None:
                self.visit(v)

        self.visit(node.name)
        self.add_feature(f"ArrayDecl(dim={len(node.dim)})")

    def visit_PragmaDir(self, node):
        self.add_feature(f"PragmaDir")

    def visit_Label(self, node):
        self.add_feature(f"Label")

    def _visit_args(self, arglist):
        sa = []
        for a in arglist:
            if isinstance(a, pa.Node):
                sa.append(self.visit(a))
            elif isinstance(a, ptxtokens.BinFloat):
                assert False, f"Legacy, shouldn't happen"
                # this needs to be handled better by converting
                # BinFloat to a proper AST node, perhaps a Constexpr
                # with only it.
                sa.append(a.value)
            else:
                raise NotImplementedError(f"Unknown type of argument {a}")

    def visit_CallStmt(self, node):
        out = []
        if node.predicate: self.visit(node.predicate)
        self.add_feature("CallStmt")

        args = []
        if node.ret_params:
            self.add_feature("CallStmt" + f"(ret_params={len(node.ret_params)})")
            self._visit_args(node.ret_params)

        self.visit(node.func)

        if node.params:
            self.add_feature("CallStmt" + f"(params={len(node.params)})")
            self._visit_args(node.params)

        if node.targets:
            self.add_feature("CallStmt" + f"(targets)")
            self.visit(node.targets)

    def visit_Statement(self, node):
        if node.predicate: self.visit(node.predicate)
        opcode = "".join(utils.dfs_token_list_rec(node.opcode))
        self._visit_args(node.args)
        # TODO: remove type information?
        self.add_feature(f"Statement(opcode={opcode})")

    def visit_Block(self, node):
        self._enter_block()
        self.add_feature(f"Block(depth={self.indent})")
        self.generic_visit(node)
        self._exit_block()

    def visit_Alias(self, node):
        self.visit(node.falias)
        self.visit(node.aliasee)
        self.add_feature("Alias")

    def visit_CallPrototype(self, node):
        features = []

        if node.ret_params:
            map(self.visit, node.ret_params)
            features.append(f"ret_params={len(node.ret_params)}")

        if node.params:
            map(self.visit, node.params)
            features.append(f"params={len(node.params)}")

        if node.noreturn:
            features.append("noreturn")

        features = ", ".join(features)
        if len(features): features = "(" + features + ")"
        self.add_feature(f"CallPrototype{features}")

    def visit_Func(self, node):
        features = []

        if node.ret_params:
            map(self.visit, node.ret_params)
            features.append(f"ret_params={len(node.ret_params)}")

        if node.params:
            map(self.visit, node.params)
            features.append(f"params={len(node.params)}")

        if node.noreturn:
            features.append("noreturn")

        if node.body:
            self.visit(node.body)
            features.append("body")
        else:
            features.append("emptybody")

        features = ", ".join(features)
        if len(features): features = "(" + features + ")"
        self.add_feature(f"Func{features}")

    def visit_EntryDir(self, node):
        for p in node.args:
            self.visit(p)

        self.add_feature(f"EntryDir({node.name})")

    def visit_Entry(self, node):
        self.visit(node.name)
        if node.params:
            map(self.visit, node.params)

            self.add_feature(f"Entry(params={len(node.params)})")
        else:
            self.add_feature(f"Entry")

        if node.directives:
            for x in node.directives:
                self.visit(x)

        self.visit(node.body)

    def visit_Linker(self, node):
        self.add_feature(f"Linker({node.directive})")
        self.visit(node.identifier)

    def visit_Target(self, node):
        for t in node.targets:
            self.add_feature(f"Target({t})")

        if node.address_size:
            self.add_feature(f"Target(address_size={node.address_size})")

    def visit_Module(self, node):
        self.add_feature(f"Module(version={node.version})")
        self.generic_visit(node)

    def visit(self, node):
        super().visit(node)
        assert self._method_cache[node.__class__.__name__] is not self.generic_visit, f"Unimplemented visitor: {node.__class__.__name__}"

