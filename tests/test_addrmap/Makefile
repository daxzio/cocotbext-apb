SIM?=icarus
TOPLEVEL_LANG=verilog
WORK_BASE?=..

TOPLEVEL = regblock
MODULE = test_dut
REGWIDTH?=32

INT_VERILOG_SOURCES += \
    ./regblock_${REGWIDTH}.sv \

COCOTB_SOURCES = \

include ${WORK_BASE}/rtlflo/cocotb_helper.mak

CPUIF?=apb4-flat
RDL_ARGS?=-P REGWIDTH=${REGWIDTH}
include ../regblock.mak

# make clean etana REGWIDTH=8 ; cp regblock.sv regblock_8.sv ; make sim REGWIDTH=8
# make clean etana REGWIDTH=16 ; cp regblock.sv regblock_16.sv ; make sim REGWIDTH=16
# make clean etana REGWIDTH=32 ; cp regblock.sv regblock_32.sv ; make sim REGWIDTH=32
