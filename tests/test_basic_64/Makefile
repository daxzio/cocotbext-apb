SIM?=icarus
TOPLEVEL_LANG=verilog
WORK_BASE?=..
BASE?=etana
# PROJ_HOME?=..

TOPLEVEL = dut
MODULE = test_${TOPLEVEL}

INT_VERILOG_SOURCES += \
    ../rtl/top_64.sv \

COCOTB_SOURCES = \
    ./dut.sv

GENERICS?= \
    REGWIDTH=64 \
    N_REGS=32

include ${WORK_BASE}/rtlflo/cocotb_helper.mak
