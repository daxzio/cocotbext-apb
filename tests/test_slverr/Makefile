SIM?=icarus
TOPLEVEL_LANG=verilog
WORK_BASE?=..

TOPLEVEL = regblock
MODULE = test_dut

INT_VERILOG_SOURCES += \
    ./regblock.sv \

COCOTB_SOURCES = \

include ${WORK_BASE}/rtlflo/cocotb_helper.mak

etana:
	peakrdl etana regblock.rdl -o ./ --cpuif apb4-flat --err-if-bad-addr --err-if-bad-rw --rename regblock

regblock:
	peakrdl regblock regblock.rdl -o ./ --cpuif apb4-flat --err-if-bad-addr --err-if-bad-rw --rename regblock
