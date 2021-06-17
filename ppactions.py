from ptxgenactions import *
from ptxast import *
from ebnftools.convert.ply import utils
from ptxtokens import *

class ChooseMixin:
    """Used to handle rules that are only choices"""
    def abstract(self):
        return self.args[0]

class a_ce_int_literal(a_ce_int_literal):
    def abstract(self):
        return IntLiteral(self.args[0].value, self.args[0].unsigned)

class a_ce_dbl_literal(a_ce_dbl_literal):
    def abstract(self):
        return DblLiteral(self.args[0].value)

class a_ce_literal(a_ce_literal):
    def abstract(self):
        return self.args[0]

class a_ce_unary_1(a_ce_unary_1):
    def abstract(self):
        if self.args[0] is None:
            return self.args[1]

        x = self.args[1]
        for op in reversed(list(utils.make_concat_list(self.args[0]))):
            if not isinstance(op, str):
                op = ''.join(utils.dfs_token_list(op))

            x = UnOp(op=op, expr=x)

        return x

class a_ce_primary(a_ce_primary):
    def abstract(self):
        if self.args[1] is None:
            return self.args[0]

        if isinstance(self.args[1], Node):
            return self.args[1]
        else:
            return Cast(self.args[1].args[0], self.args[3])

class a_predicate(a_predicate):
    def abstract(self):
        return Predicate(self.args[1] is not None, self.args[2])

class a_label(a_args):
    def abstract(self):
        return Label(self.args[0].value)

class a_args(a_args):
    def abstract(self):
        return self.args[0]

class a_arg_list(a_arg_list):
    def abstract(self):
        if self.args[0] is None:
            args = []
        else:
            args = [self.args[0].args[0]]
            args.extend(utils.make_concat_list(self.args[0].args[1], sel=[1]))

        return args

class a_pragma(ChooseMixin, a_pragma):
    pass

class a_pragma_list(a_pragma_list):
    def abstract(self):
        a = [self.args[0]]
        a.extend(utils.make_concat_list(self.args[1], sel=[1]))
        return  a

class a_pragma_dir(a_pragma_dir):
    def abstract(self):
        return Pragma(self.args[1])

class a_label(a_label):
    def abstract(self):
        # shift/reduce issue?
        if isinstance(self.args[0], Iden):
            return Label(self.args[0].value)
        else:
            assert isinstance(self.args[0], str)
            return Label(self.args[0])

class a_pragma_stmt(a_pragma_stmt):
    def abstract(self):
        return self.args[0]

class a_statement(a_statement):
    def abstract(self):
        return Statement(self.args[0], self.args[1], self.args[2])

class BinOpMixin:
    def abstract(self):
        if self.args[0] is None:
            return self.args[1]

        op = self.args[0].args[1]
        if not isinstance(op, str):
            # this is a list of alt operators
            op = utils.dfs_token_list(op)[0]

        return BinOp(op, self.args[0].args[0], self.args[1])

class a_ce_lor(BinOpMixin,a_ce_lor):
    pass
class a_ce_land(BinOpMixin,a_ce_land):
    pass
class a_ce_bor(BinOpMixin,a_ce_bor):
    pass
class a_ce_band(BinOpMixin,a_ce_band):
    pass
class a_ce_bxor(BinOpMixin,a_ce_bxor):
    pass
class a_ce_eq(BinOpMixin,a_ce_eq):
    pass
class a_ce_cmp(BinOpMixin,a_ce_cmp):
    pass
class a_ce_shifts(BinOpMixin,a_ce_shifts):
    pass
class a_ce_sum(BinOpMixin,a_ce_sum):
    pass

class a_ce_prod(BinOpMixin,a_ce_prod):
    pass

class a_ce_unary_2(a_ce_unary_2):
    def abstract(self):
        return self.args[0]

class a_constexpr(a_constexpr):
    def abstract(self):
        return ConstExpr(self.args[0])

class a_ce_ternary(a_ce_ternary):
    def abstract(self):
        if self.args[1] is None:
            return self.args[0]

        return Ternary(self.args[0], self.args[2], self.args[4])

class a_target_list(a_target_list):
    def abstract(self):
        args = [self.args[0]]
        args.extend(utils.make_concat_list(self.args[1], sel=[1]))
        # keep this as a list of strings
        return [x.value for x in args]

class a_toplevel_statements(a_toplevel_statements):
    def abstract(self):
        return self.args[0]

class a_param_list(a_param_list):
    def abstract(self):
        args = [self.args[0]]
        args.extend(utils.make_concat_list(self.args[1], sel=[1]))
        return args

class a_param_spec(a_param_spec):
    def abstract(self):
        return self.args[1]

class a_block_stmt(ChooseMixin, a_block_stmt):
    pass

class a_unsigned(ChooseMixin, a_unsigned):
    pass

class a_signed(ChooseMixin, a_signed):
    pass

class a_signed_unsigned(ChooseMixin, a_signed_unsigned):
    pass

class a_fbus_type(ChooseMixin, a_fbus_type):
    pass

class a_binary(ChooseMixin, a_binary):
    pass

class a_float(ChooseMixin, a_float):
    pass

class a_ld_type(ChooseMixin, a_ld_type):
    pass

class a_st_type(ChooseMixin, a_st_type):
    pass

class a_cc_type(ChooseMixin, a_cc_type):
    pass

class a_half_float(ChooseMixin, a_half_float):
    pass

class a_opcodes(ChooseMixin, a_opcodes):
    pass

class a_ptx_types(ChooseMixin, a_ptx_types):
    pass

class a_block(a_block):
    def abstract(self):
        return Block(body=list(utils.make_concat_list(self.args[1])))

class a_var_parametric(a_var_parametric):
    def abstract(self):
        return ParametricVarname(self.args[0].value, self.args[2].value)

class a_varname(ChooseMixin, a_varname):
    pass

class a_start(a_start):
    def abstract(self):
        self.args[1] = list(utils.make_concat_list(self.args[1]))
        # version is set externally
        return Module(version=None, target=self.args[0], body=self.args[1])

class a_address_size_dir(a_address_size_dir):
    def abstract(self):
        assert isinstance(self.args[1], Decimal)
        return self.args[1].value

class a_target_dir(a_target_dir):
    def abstract(self):
        return Target(targets=self.args[1], address_size=self.args[2])

class a_generic_var(a_generic_var):
    def abstract(self):
        assert self.args[0].name == "generic"  # ID
        return Generic(self.args[2])

class a_addr_expr_offset(a_addr_expr_offset):
    def abstract(self):
        return self.args[1]

class a_addr_expr(a_addr_expr):
    def abstract(self):
        return AddrExpr(var=self.args[0].args[0], offset=self.args[1])

class a_addr_operand(a_addr_operand):
    def abstract(self):
        # TODO: handle immediate 32-bit addresses
        return AddressOpr(value=self.args[1], offset=self.args[2].args[1] if self.args[2] else None)

class a_linker_identifier(ChooseMixin, a_linker_identifier):
    pass

class a_param_state_spaces(ChooseMixin, a_param_state_spaces):
    pass

class a_linker_stmt(a_linker_stmt):
    def abstract(self):
        return Linker(directive=self.args[0].args[0], identifier=self.args[1])

class a_param_decl(a_param_decl):
    def abstract(self):
        return Param(self.args[0], self.args[1], self.args[2], self.args[3], self.args[4])

class a_varinit_list(a_varinit_list):
    def abstract(self):
        if self.args[2] is None:
            return [VarInit(self.args[0], self.args[1])]
        else:
            a2 = utils.make_concat_list(self.args[2], sel=[1])
            x = [VarInit(self.args[0], self.args[1])]
            x.extend(a2)
            return x

class a_array_decl(a_array_decl):
    def abstract(self):
        dim = list(utils.make_concat_list(self.args[1], sel=[1]))
        return ArrayDecl(name=self.args[0], dim=dim)

class a_iden(a_iden):
    def abstract(self):
        return Id(name=self.args[0].value)

class a_var_decl(a_var_decl):
    def abstract(self):
        return MultivarDecl(self.args[0], self.args[1], self.args[2], self.args[3], self.args[4])

class a_var_decl_stmt(a_var_decl_stmt):
    def abstract(self):
        return self.args[0]

class a_vector_suffixes(ChooseMixin, a_vector_suffixes):
    pass

class a_align_dir(a_align_dir):
    def abstract(self):
        return self.args[1].value

class a_vector_extract(a_vector_extract):
    def abstract(self):
        return VectorComp(self.args[0], self.args[1])

class a_vector_operand(a_vector_operand):
    def abstract(self):
        elts = [self.args[1]]
        elts.extend(utils.make_concat_list(self.args[2], sel=[1]))
        return VectorOpr(elts)

class a_call_rp_list(a_call_rp_list):
    def abstract(self):
        return self.args[1]

class a_call_ret(a_call_ret):
    def abstract(self):
        if self.args[0]:
            return self.args[0].args[0]

class a_call_param(a_call_param):
    def abstract(self):
        if self.args[0]:
            return self.args[0].args[1]

class a_call_fproto_flist(a_call_fproto_flist):
    def abstract(self):
        if self.args[0]:
            return self.args[0].args[1]

class a_call_stmt(a_call_stmt):
    def abstract(self):
        return CallStmt(predicate=self.args[0],
                        opcode=''.join([self.args[1], '.uni' if self.args[2] else '']),
                        ret_params=self.args[3],
                        func=self.args[4],
                        params=self.args[5],
                        targets=self.args[6])

class a_func_body(a_func_body):
    def abstract(self):
        return self.args[0]

class a_scalar_init(a_scalar_init):
    def abstract(self):
        return self.args[0]

class a_varinitializer(a_varinitializer):
    def abstract(self):
        return self.args[1].args[0]

class a_array_elem(ChooseMixin, a_array_elem):
    pass

class a_array_elem_list(a_array_elem_list):
    def abstract(self):
        return [self.args[0]] + list(utils.make_concat_list(self.args[1], sel=[1]))

class a_array_init(a_array_init):
    def abstract(self):
        return ArrayLiteral(elts=self.args[1])

# class a_bitbucket_arg(a_bitbucket_arg):
#     def abstract(self):
#         return BitbucketArg()

class a_negated_arg(a_negated_arg):
    def abstract(self):
        return NegatedArg(self.args[1])

class a_paired_arg(a_paired_arg):
    def abstract(self):
        return PairedArg(args=(self.args[0], self.args[2]))

class a_func(a_func):
    def abstract(self):
        return Func(name=self.args[2], ret_params=self.args[1], params=self.args[3],
                    noreturn=self.args[4] is not None, body=self.args[5])

class a_dim_list(a_dim_list):
    def abstract(self):
        a = [self.args[0]]
        if self.args[1]: a.append(self.args[1].args[1])
        if self.args[2]: a.append(self.args[2].args[1])
        return a

class a_entry_dir_list(a_entry_dir_list):
    def abstract(self):
        if self.args[0]:
            return list(utils.make_concat_list(self.args[0]))

class a_entry_dir(a_entry_dir):
    def abstract(self):
        a = self.args[0].args[1]
        if not isinstance(a, list): a = [a]
        return EntryDir(self.args[0].args[0], a)

class a_entry(a_entry):
    def abstract(self):
        return Entry(name=self.args[1], params=self.args[2], directives=self.args[3], body=self.args[4])

class a_tex_xps_operand(a_tex_xps_operand):
    # explicit sampler
    def abstract(self):
        return TexCoordOpr(texref=self.args[1], sampler=self.args[3], texcoord=self.args[5])

class a_tex_imps_operand(a_tex_imps_operand):
    # implicit sampler
    def abstract(self):
        return TexCoordOpr(texref=self.args[1], sampler=None, texcoord=self.args[3])

class a_tex_coord(ChooseMixin,a_tex_coord):
    pass

class a_tex_coord_operand(ChooseMixin,a_tex_coord_operand):
    pass

class a_label_list_entry(ChooseMixin, a_label_list_entry):
    pass

class a_label_list(a_label_list):
    def abstract(self):
        a = [self.args[0]]
        a.extend(utils.make_concat_list(self.args[1], sel=[1]))
        return a

class a_branchtargets_stmt(a_branchtargets_stmt):
    def abstract(self):
        return BranchTargets(self.args[1])

class a_sel_op(ChooseMixin, a_sel_op):
    pass

class a_vmad_neg_op(a_vmad_neg_op):
    def abstract(self):
        x = self.args[1].args[0]
        if isinstance(x, Id):
            return SelOpr(x, '', negate=True)
        else:
            assert isinstance(x, SelOpr)
            x.negate = True
            return x

class a_vmad_stmt(a_vmad_stmt):
    def abstract(self):
        return Statement(predicate = self.args[0],
                         opcode=self.args[1],
                         args=[self.args[2], self.args[4], self.args[6], self.args[8]])

class a_vmad_op(ChooseMixin, a_vmad_op):
    pass

class a_reg_sel_op(a_reg_sel_op):
    def abstract(self):
        return SelOpr(self.args[0], self.args[1], negate=False)

class a_dwarf_int_list(a_dwarf_int_list):
    def abstract(self):
        a = [self.args[0]]
        a.extend(utils.make_concat_list(self.args[1], sel=[1]))
        return a

class a_dwarf_label(a_dwarf_label):
    def abstract(self):
        offset = None if self.args[1] is None else self.args[1].args[1]
        return DwarfLabel(self.args[0].args[0], offset)

class a_dwarf_lines(a_dwarf_lines):
    def abstract(self):
        return DwarfLine(self.args[0], self.args[1])

class a_section_dir(a_section_dir):
    def abstract(self):
        return SectionDir(self.args[1].args[0], list(utils.make_concat_list(self.args[3])))

class a_filename(a_filename):
    def abstract(self):
        return self.args[0]

class a_fileinfo(a_fileinfo):
    def abstract(self):
        return (self.args[1].value, self.args[3].value)

class a_file_dir(a_file_dir):
    def abstract(self):
        return File(index=self.args[1].value,
                    name=self.args[2],
                    timestamp_size=self.args[3])

class a_function_list(a_function_list):
    def abstract(self):
        a = [self.args[0]]
        a.extend(utils.make_concat_list(self.args[1], sel=[1]))
        return a

class a_calltargets_dir(a_calltargets_dir):
    def abstract(self):
        return CallTargets(self.args[1])

class a_loc_dir(a_loc_dir):
    def abstract(self):
        return Loc(self.args[1].value,
                   self.args[2].value,
                   self.args[3].value)

class a_callprototype_dir(a_callprototype_dir):
    def abstract(self):
        assert self.args[2].name == "_", f".callprototype syntax error"
        return CallPrototype(self.args[1], self.args[3], noreturn=self.args[4] is not None)

class a_alias_dir(a_alias_dir):
    def abstract(self):
        return Alias(self.args[1], self.args[3])
