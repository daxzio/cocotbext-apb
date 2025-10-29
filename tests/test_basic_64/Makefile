SIM?=icarus
TOPLEVEL_LANG=verilog
WORK_BASE?=..

TOPLEVEL = regblock
MODULE = test_dut

INT_VERILOG_SOURCES += \
    ./regblock.sv \

COCOTB_SOURCES = \

include ${WORK_BASE}/rtlflo/cocotb_helper.mak

CPUIF?=apb4-flat
RDL_ARGS?=-P N_REGS=32 -P REGWIDTH=64
include ../regblock.mak
