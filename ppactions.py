from ptxgenactions import *
from ptxast import *

class a_ce_int_literal(a_ce_int_literal):
    def abstract(self):
        return IntLiteral(self.args[0].value, self.args[0].unsigned)

class a_ce_literal(a_ce_literal):
    def abstract(self):
        return self.args[0]

class a_bnf_concat_ce_unary_1(a_bnf_concat_ce_unary_1):
    def abstract(self):
        if self.args[0] is None:
            return None

        return self

class a_ce_unary_1(a_ce_unary_1):
    def abstract(self):
        if self.args[0] is None:
            return self.args[1]

        return Unop(op=self.args[0].args[0], expr=self.args[1])

class a_ce_primary(a_ce_primary):
    def abstract(self):
        if self.args[1] is None:
            return self.args[0]

        return self

class BinOpMixin:
    def abstract(self):
        if self.args[0].args[0] is None:
            return self.args[1]

        return BinOp(self.args[0].args[1], self.args[0].args[0], self.args[1])

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
        return self.args[0]

class a_ce_ternary(a_ce_ternary):
    def abstract(self):
        if self.args[1] is None:
            return self.args[0]

        return self
