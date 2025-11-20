TOPLEVEL_LANG?=verilog
TOPLEVEL?=dut
COCOTB_TEST_MODULES?=test_dut

ifeq ($(TOPLEVEL_LANG),verilog)
    WAVES=1
endif
# COCOTB_RESOLVE_X?=ZEROS
# export COCOTB_RESOLVE_X

ifneq (,$(wildcard ./makefile_synth.mak))
default: vivado_build
SIM?=icarus
else
default: sim
ifeq ($(SIM),icarus)
sim: clean_sim_build
.PHONY: clean_sim_build
clean_sim_build:
	rm -rf sim_build
endif
endif


include $(shell cocotb-config --makefiles)/Makefile.sim
include ${WORK_BASE}/rtlflo/xilinx_helper.mak
include ${WORK_BASE}/rtlflo/verible_helper.mak
include ${WORK_BASE}/rtlflo/git_helper.mak

# DEFINES += COCOTB_RUNNING=1
export COCOTB_RUNNING
ifeq ($(TOPLEVEL_LANG),verilog)
	ifeq ($(SIM), icarus)
        DEFINES += COCOTB_ICARUS=1
	else ifeq ($(SIM), ius)
        DEFINES += COCOTB_CADENCE=1
        DEFINES += COCOTB_IUS=1
		COMPILE_ARGS += -disable_sem2009
		COMPILE_ARGS += -sv
		COMPILE_ARGS += -top ${TOPLEVEL}
	else ifeq ($(SIM),xcelium)
        DEFINES += COCOTB_CADENCE=1
        DEFINES += COCOTB_XCELIUM=1
		COMPILE_ARGS += -disable_sem2009
		COMPILE_ARGS += -sv
		COMPILE_ARGS += -top ${TOPLEVEL}
	else ifeq ($(SIM),verilator)
        DEFINES += COCOTB_VERILATOR=1
		COMPILE_ARGS += --no-timing -Wno-WIDTHEXPAND -Wno-WIDTHTRUNC -Wno-STMTDLY
# 		COMPILE_ARGS += --public
# 		COMPILE_ARGS += --public-flat-rw
# 		COMPILE_ARGS += --public-depth 10 --hierarchical -j 8 --public-flat-rw
# 	    EXTRA_ARGS += --public-depth 10
# 		PLUSARGS += --public-depth 10
	endif
endif

ifeq ($(WAVES),1)
    DEFINES += COCOTB_WAVES=1
#     WAVES=1
	ifeq ($(SIM),verilator)
		COCOTB_PLUSARGS += --trace
		EXTRA_ARGS += --trace # vcd format
		EXTRA_ARGS += --trace-fst
		EXTRA_ARGS += --trace-structs
	endif
endif


# Process generics
ifeq ($(TOPLEVEL_LANG),verilog)
	ifeq ($(SIM), icarus)
	    COMPILE_ARGS += $(addprefix -P${TOPLEVEL}., $(GENERICS))
	else ifneq ($(filter $(SIM),questa modelsim riviera activehdl),)
	    SIM_ARGS += $(addprefix -g, $(GENERICS))
	else ifeq ($(SIM),vcs)
	    COMPILE_ARGS += $(addprefix -pvalue+/, $(GENERICS))
	else ifeq ($(SIM),verilator)
	    COMPILE_ARGS += $(addprefix -G, $(GENERICS))
	else ifneq ($(filter $(SIM),ius xcelium),)
	    EXTRA_ARGS += $(addprefix -defparam ${TOPLEVEL}., $(GENERICS))
	endif
else ifeq ($(TOPLEVEL_LANG),vhdl)
    ifneq ($(filter $(SIM),ghdl questa modelsim riviera activehdl),)
        # ghdl, questa, and aldec all use SIM_ARGS with '-g' for setting generics
        SIM_ARGS += $(addprefix -g, $(GENERICS))
    else ifneq ($(filter $(SIM),ius xcelium),)
        SIM_ARGS += $(addprefix -generic \"${TOPLEVEL}:, $(addsuffix \", $(subst =,=>, $(GENERICS))))
    endif
else
    $(error "A valid value (verilog or vhdl) was not provided for TOPLEVEL_LANG=$(TOPLEVEL_LANG)")
endif

# Process defines
ifeq ($(TOPLEVEL_LANG),verilog)
	ifeq ($(SIM), icarus)
	    COMPILE_ARGS += $(addprefix -D , $(DEFINES))
	else ifneq ($(filter $(SIM),questa modelsim riviera activehdl),)
	    #SIM_ARGS += $(addprefix -g, $(GENERICS))
	else ifeq ($(SIM),vcs)
	    #COMPILE_ARGS += $(addprefix -pvalue+/, $(GENERICS))
	else ifeq ($(SIM),verilator)
	    EXTRA_ARGS += $(addprefix -D, $(DEFINES))
	else ifneq ($(filter $(SIM),ius xcelium),)
	    EXTRA_ARGS += $(addprefix -define , $(DEFINES))
	endif
else ifeq ($(TOPLEVEL_LANG),vhdl)
    ifneq ($(filter $(SIM),ghdl questa modelsim riviera activehdl),)
        #SIM_ARGS += $(addprefix -g, $(GENERICS))
    else ifneq ($(filter $(SIM),ius xcelium),)
        #SIM_ARGS += $(addprefix -generic \"${TOPLEVEL}:, $(addsuffix \", $(subst =,=>, $(GENERICS))))
    endif
else
    $(error "A valid value (verilog or vhdl) was not provided for TOPLEVEL_LANG=$(TOPLEVEL_LANG)")
endif

VERILOG_DESIGN?=\
    ${SIM_VERILOG_SOURCES} \
    ${XILINX_SIM_SOURCES} \
    ${EXT_VERILOG_SOURCES} \
    ${INT_VERILOG_SOURCES}

VERILOG_SOURCES+=\
    ${VERILOG_DESIGN} \
    ${COCOTB_SOURCES}

VHDL_SOURCES += \
    ${INT_VHDL_SOURCES} \
    ${EXT_VHDL_SOURCES}

${CDSLIB}:
	echo "include \$${INCISIVE_HOME}/tools.lnx86/inca/files/cds.lib" > ${CDSLIB}

cdslib:: ${CDSLIB}

all_libs_clean::
	@rm -rf ${CDSLIB}

waves:
ifeq ($(SIM), icarus)
	gtkwave sim_build/*.fst &
else ifeq ($(SIM), ius)
	simvision -waves waves.shm &
else ifeq ($(SIM),verilator)
	gtkwave dump.fst &
endif

clean::
	rm -rf __pycache__/ .simvision/ .Xil/ results.xml *.trn *.dsn vivado* *.vcd *.out irun* simvision* xrun* .bpad/ waves.shm/ *.err INCA_libs/ *.fst* ncvlog.log combined_results.xml
