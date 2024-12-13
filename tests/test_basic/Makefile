SIM?=icarus
TOPLEVEL_LANG=verilog
WORK_BASE?=..
BASE?=etana
# PROJ_HOME?=..

TOPLEVEL = dut
MODULE = test_${TOPLEVEL}

INT_VERILOG_SOURCES += \
    ../rtl/top.sv \

COCOTB_SOURCES = \
    ./dut.sv

include ${WORK_BASE}/rtlflo/cocotb_helper.mak
