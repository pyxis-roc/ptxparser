#!/usr/bin/env python

# SPDX-FileCopyrightText: 2021,2023 University of Rochester
#
# SPDX-License-Identifier: LGPL-3.0-or-later

#
# predefined.py
#
# Definitions that are pre-defined in PTX

import ptxparser
import re

PTX_COMMENT_RE = re.compile(r"//.*$", re.MULTILINE)

# from section 10 of the PTX docs
# we use // for comments for convenience
PREDEFINED_PTX_65 = """
.version 6.5
.target sm_61

.sreg .v4 .u32 %tid;
// .sreg .u32 %tid.x, %tid.y, %tid.z;

.sreg .v4 .u32 %ntid;                   // CTA shape vector
// .sreg .u32 %ntid.x, %ntid.y, %ntid.z;   // CTA dimensions

.sreg .u32 %laneid;
.sreg .u32 %warpid;

.sreg .v4 .u32 %ctaid;                      // CTA id vector
// .sreg .u32 %ctaid.x, %ctaid.y, %ctaid.z;    // CTA id components

.sreg .v4 .u32 %nctaid;                      // Grid shape vector
// .sreg .u32 %nctaid.x,%nctaid.y,%nctaid.z;   // Grid dimensions

.sreg .u32 %smid;
.sreg .u32 %nsmid;

.sreg .u64 %gridid;
.sreg .u32 %lanemask_eq;
.sreg .u32 %lanemask_le;
.sreg .u32 %lanemask_lt;
.sreg .u32 %lanemask_ge;
.sreg .u32 %lanemask_gt;

.sreg .u32 %clock;
.sreg .u32 %clock_hi;

.sreg .u64 %clock64;

.sreg .u32 %pm<8>;

.sreg .u64 %pm0_64;
.sreg .u64 %pm1_64;
.sreg .u64 %pm2_64;
.sreg .u64 %pm3_64;
.sreg .u64 %pm4_64;
.sreg .u64 %pm5_64;
.sreg .u64 %pm6_64;
.sreg .u64 %pm7_64;

.sreg .b32 %envreg<32>;

.sreg .u64 %globaltimer;
.sreg .u32 %globaltimer_lo, %globaltimer_hi;

.sreg .u32 %total_smem_size;
.sreg .u32 %dynamic_smem_size;
"""


def parse_predefined(predef):
    predef = PTX_COMMENT_RE.sub("", predef)
    ast = ptxparser.ptx_parse(predef)
    return ast
