// Copyright 2009-2021 NTESS. Under the terms
// of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.
//
// Copyright (c) 2009-2021, NTESS
// All rights reserved.
//
// Portions are copyright of other developers:
// See the file CONTRIBUTORS.TXT in the top level directory
// the distribution for more information.
//
// This file is part of the SST software package. For license
// information, see the LICENSE file in the top level directory of the
// distribution.

#ifndef _H_VANADIS_INST_ALL
#define _H_VANADIS_INST_ALL

// Arithmetic operations
#include "inst/vadd.h"
#include "inst/vaddi.h"
#include "inst/vaddiu.h"
#include "inst/vsub.h"
#include "inst/vmul.h"
#include "inst/vmuli.h"
#include "inst/vmulsplit.h"
#include "inst/vdivmod.h"

// Logical operations
#include "inst/vand.h"
#include "inst/vandi.h"
#include "inst/vnor.h"
#include "inst/vor.h"
#include "inst/vori.h"
#include "inst/vxor.h"
#include "inst/vxori.h"

// Shift operations
#include "inst/vsll.h"
#include "inst/vslli.h"
#include "inst/vsra.h"
#include "inst/vsrai.h"
#include "inst/vsrl.h"
#include "inst/vsrli.h"

// Compare operations
#include "inst/vscmp.h"
#include "inst/vscmpi.h"
#include "inst/vbcmpi.h"
#include "inst/vbcmpil.h"

// Jumps and PC change instructions
#include "inst/vjump.h"
#include "inst/vjlr.h"
#include "inst/vjl.h"
#include "inst/vjr.h"
#include "inst/vbcmp.h"
#include "inst/vbfp.h"

// Load instructions
#include "inst/vload.h"
#include "inst/vpartialload.h"

// Store instructions
#include "inst/vstore.h"
#include "inst/vpartialstore.h"

// Fence Instructions
#include "inst/vfence.h"

// Special instructions
#include "inst/vdecodefaultinst.h"
#include "inst/vnop.h"
#include "inst/vsetreg.h"
#include "inst/vsyscall.h"

// FP Convert/Move
#include "inst/vfp2gpr.h"
#include "inst/vgpr2fp.h"
#include "inst/vfp2fp.h"
#include "inst/vfpconv.h"

// FP Arith
#include "inst/vfpmul.h"
#include "inst/vfpadd.h"
#include "inst/vfpsub.h"
#include "inst/vfpscmp.h"
#include "inst/vfpdiv.h"

// Truncate
#include "inst/vtrunc.h"

#endif
