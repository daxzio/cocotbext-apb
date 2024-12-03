XILINX_REV ?= 2021.2
MAKE_XILINX_LIB ?= C:\modelsim_lib
XILINX_VIVADO?=C:\Xilinx\Vivado\${XILINX_REV}
RTLFLOW_PATH?=../rtlflow
TEST ?= 
FPGA_BIT ?= $(shell ${RTLFLOW_PATH}/vivado_runner.py bitfile)
FPGA_BIT_BCK ?= $(shell ${RTLFLOW_PATH}/vivado_runner.py date_fpga)
BCK_DIR ?= ../bitstreams

ifeq ($(XILINX_REV),)
    export XILINX_REV=${XILINX_REV}
endif
ifeq ($(XILINX_LIB),)
    export XILINX_LIB=${MAKE_XILINX_LIB}
endif
ifeq ($(VIVADO_PATH),)
    export VIVADO_PATH=${XILINX_VIVADO}
endif

build: vivado_build

run:
	python ${RTLFLOW_PATH}/run_tb.py ${TEST}
    
vunit_version:
	python ${RTLFLOW_PATH}/run_tb.py --version
    
gui:
	python ${RTLFLOW_PATH}/run_tb.py -g ${TEST}

clean:	
	rm -rf *.bak *.log *.jou __pycache__ vunit_out work .Xil *.cbf .cxl* vivado*str *.tmp xpr*/
	#python run_tb.py --clean

license:
	lmutil lmstat -a

vivado_version:
	${VIVADO_PATH}/bin/vivado -version

vivado_libs:
	rm -rf modelsim.ini
	${VIVADO_PATH}/bin/vivado -mode batch -source ${RTLFLOW_PATH}/compile_libs.tcl

vivado_build:
	python ${RTLFLOW_PATH}/vivado_runner.py build
	${VIVADO_PATH}/bin/vivado -mode batch -source build_design.tcl


vivado_synth:
	python ${RTLFLOW_PATH}/vivado_runner.py synth
	${VIVADO_PATH}/bin/vivado -mode batch -source synth_design.tcl

synth: vivado_synth

vivado_run:
	python ${RTLFLOW_PATH}/vivado_runner.py run
	${VIVADO_PATH}/bin/vivado -mode batch -source run_design.tcl

vivado:
	python ${RTLFLOW_PATH}/vivado_runner.py build
	${VIVADO_PATH}/bin/vivado -mode batch -source build_design.tcl
	python ${RTLFLOW_PATH}/vivado_runner.py run
	${VIVADO_PATH}/bin/vivado -mode batch -source run_design.tcl


.PHONY : help
help : 
	@echo "    help               : List all commands"
	@echo "    clean              : Clean up all working file"
	@echo "    run <default>      : Compile and run command line all tests"
	@echo "    run TEST=testname  : Compile and run command line single test"
	@echo ""
	@echo "        make run TEST=work.tb_xs.test_004"
	@echo ""
	@echo "    gui                : Compile and start GUI mode for all tests"
	@echo "    gui TEST=testname  Compile and run command line single test"
	@echo ""
	@echo "        make gui TEST=work.tb_xs.test_004"
	@echo ""
	@echo "    license            : Return the status of the license servers"
	@echo "    vivado_version     : Return the version of vivado found"
	@echo "    vivado_libs        : Compile xilinx libraries under modelsim"
	@echo "    vivado_build       : Build the vivado project from scratch"
	@echo "    vivado_synth       : Synthesise the vivado project"
	@echo "    vivado_run         : Compile and generate the vivado project"
	@echo "    vivado             : A vivado_build followed by vivado_run"

