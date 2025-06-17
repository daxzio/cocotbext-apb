XILINX_REV?=2021.2
XILINX_PART?=xc7a100tcsg324-1
CDSLIB?=./cds_${SIM}.lib
COMPILE_LIBS?=../../libs
RTLFLO_PATH?=../../rtlflo

XILINX_LIB=${COMPILE_LIBS}/${SIM}/xilinx
ifneq ($(XILINX_VIVADO),)
XILINX_BASE?=${XILINX_VIVADO}/data
XILINX_LIB=${COMPILE_LIBS}/${SIM}/xilinx-${XILINX_REV}
endif
ifeq ($(SIM),xcelium)
CADENCE_VLOG?=xmvlog
CADENCE_VHDL?=xmvhdl
else
CADENCE_VLOG?=ncvlog
CADENCE_VHDL?=ncvhdl
endif

ifneq (${USE_CDS},)
    ifeq ($(SIM),xcelium)
		COMPILE_ARGS += -cdslib ${CDSLIB}
	else ifeq ($(SIM),ius)
		COMPILE_ARGS += -cdslib ${CDSLIB}
    else ifeq ($(SIM),verilator)
# 	    COMPILE_ARGS += --top-module glbl
# 		VERILOG_SOURCES += \
# 			${XILINX_BASE}/verilog/src/glbl.v
# 	    VERILOG_SOURCES += ${UNISIMS}
    endif
endif

ifneq (${XILINX_BASE},)
	UNISIMS_VER_CNT=`grep -s unisims_ver ${CDSLIB} | wc -l`
	UNISIMS_VHDL_CNT=`grep -s unisim ${CDSLIB} | wc -l`

    UNISIMS = \
	    ${XILINX_BASE}/verilog/src/unisims/FDRE.v \
	    ${XILINX_BASE}/verilog/src/unisims/FDSE.v \
	    ${XILINX_BASE}/verilog/src/unisims/GND.v \
	    ${XILINX_BASE}/verilog/src/unisims/LUT1.v \
	    ${XILINX_BASE}/verilog/src/unisims/LUT2.v \
	    ${XILINX_BASE}/verilog/src/unisims/LUT3.v \
	    ${XILINX_BASE}/verilog/src/unisims/LUT4.v \
	    ${XILINX_BASE}/verilog/src/unisims/LUT5.v \
	    ${XILINX_BASE}/verilog/src/unisims/LUT6.v \
	    ${XILINX_BASE}/verilog/src/unisims/MUXF7.v \
	    ${XILINX_BASE}/verilog/src/unisims/MUXF8.v \
	    ${XILINX_BASE}/verilog/src/unisims/SRL16E.v \
	    ${XILINX_BASE}/verilog/src/unisims/SRLC32E.v \
	    ${XILINX_BASE}/verilog/src/unisims/OBUFDS.v \
	    ${XILINX_BASE}/verilog/src/unisims/BUFG.v \
	    ${XILINX_BASE}/verilog/src/unisims/IBUF.v \
	    ${XILINX_BASE}/verilog/src/unisims/MMCME2_ADV.v

    ifeq ($(SIM), icarus)
        ifneq ($(XILINX_SIM_SOURCES),)
			COMPILE_ARGS += -y${XILINX_BASE}/verilog/src/unisims
			COMPILE_ARGS += -s glbl
		    VERILOG_SOURCES += \
			    ${XILINX_BASE}/verilog/src/glbl.v
		endif
	else ifeq ($(SIM),xcelium)
		COMPILE_ARGS += -top glbl
		VERILOG_SOURCES += \
			${XILINX_BASE}/verilog/src/glbl.v
	else ifeq ($(SIM),ius)
        ifneq (${VERILOG_SOURCES},)
		    COMPILE_ARGS += -top glbl
		    VERILOG_SOURCES += \
			    ${XILINX_BASE}/verilog/src/glbl.v
		endif
    else ifeq ($(SIM),verilator)
# 	    COMPILE_ARGS += --top-module glbl
# 		VERILOG_SOURCES += \
# 			${XILINX_BASE}/verilog/src/glbl.v
# 	    VERILOG_SOURCES += ${UNISIMS}
    endif

endif

default: sim

xilinx_cdslib:
	@if [ "${UNISIMS_VHDL_CNT}" -eq "0" ]; then \
		mkdir -p ${XILINX_LIB}/unisim ; \
		mkdir -p ${XILINX_LIB}/secureip ; \
		echo "DEFINE unisim ${XILINX_LIB}/unisim" >> ${CDSLIB} ; \
		echo "DEFINE secureip ${XILINX_LIB}/secureip" >> ${CDSLIB} ; \
	fi
	@if [ "${UNISIMS_VER_CNT}" -eq "0" ]; then \
		mkdir -p ${XILINX_LIB}/unisims_ver ; \
		echo "DEFINE unisims_ver ${XILINX_LIB}/unisims_ver" >> ${CDSLIB} ; \
	fi


${XILINX_LIB}/unisims_ver: ${CDSLIB} xilinx_cdslib
	${CADENCE_VLOG} -MESSAGES -NOLOG -64bit -CDSLIB ${CDSLIB} -WORK unisims_ver ${XILINX_BASE}/verilog/src/unisims/*.v
	${CADENCE_VLOG} -MESSAGES -NOLOG -64bit -CDSLIB ${CDSLIB} -SV -WORK unisims_ver ${XILINX_BASE}/verilog/src/unisims/*.sv
	@if [ -d "${XILINX_BASE}/secureip" ]; then \
		${CADENCE_VLOG} -MESSAGES -NOLOG -64bit -CDSLIB ${CDSLIB} -WORK unisims_ver ${XILINX_BASE}/secureip/*/*.vp; \
	fi

${XILINX_LIB}/unisim: ${CDSLIB} xilinx_cdslib
	@if [ -d "${XILINX_BASE}/vhdl" ]; then \
		${CADENCE_VHDL} -MESSAGES -NOLOG -64bit -v93 -CDSLIB ${CDSLIB} -WORK unisim \
			${XILINX_BASE}/vhdl/src/unisims/unisim_VPKG.vhd \
			${XILINX_BASE}/vhdl/src/unisims/unisim_VCOMP.vhd \
			${XILINX_BASE}/vhdl/src/unisims/primitive/*.vhd ; \
		${CADENCE_VHDL} -MESSAGES -NOLOG -64bit -v93 -CDSLIB ${CDSLIB} -WORK secureip \
			${XILINX_BASE}/vhdl/src/unisims/secureip/*.vhd ;\
	fi

xilinx_lib: | ${XILINX_LIB}/unisims_ver ${XILINX_LIB}/unisim

xilinx_library:
	mkdir -p ${COMPILE_LIBS}
ifeq ($(SIM),ius)
	${MAKE} xilinx_lib
else ifeq ($(SIM),xcelium)
	${MAKE} xilinx_lib
endif

xilinx_library_clean:
	@rm -rf ${XILINX_LIB}
	@sed -in '/unisim/d' ${CDSLIB} || true
	@sed -in '/secureip/d' ${CDSLIB} || true

cdslib:: xilinx_cdslib

all_libs:: xilinx_library

all_libs_clean:: xilinx_library_clean

FPGA_DESIGN:=\
    ${XILINX_SYNTH_SOURCES} \
    ${INT_VERILOG_SOURCES} \
    ${EXT_VERILOG_SOURCES} \
    ${INT_VHDL_SOURCES} \
    ${EXT_VHDL_SOURCES}

vivado_build:
	@ export XILINX_PART="${XILINX_PART}" ; \
	export XILINX_CONSTRAINTS="${XILINX_CONSTRAINTS}" ; \
	export XILINX_CUSTOM=${XILINX_CUSTOM} ; \
	export SYNTH_TOP=${SYNTH_TOP} ; \
	export BUILD_NAME=${BUILD_NAME} ; \
	export VERILOG_INCLUDE_DIRS="${VERILOG_INCLUDE_DIRS}" ; \
	export GENERICS="${GENERICS}" ; \
	export FPGA_DESIGN="${FPGA_DESIGN}" ; \
		${RTLFLO_PATH}/vivado_helper.py

git_xilinx:
# 	git add ${PROJ_HOME}/xilinx/ip_srcs/${XILINX_PART}/${XILINX_REV}/common/common.ip_user_files/ip/*/*_sim_netlist.v -f -N --ignore-errors
	git add ${PROJ_HOME}/xilinx/ip_srcs/${XILINX_PART}/${XILINX_REV}/common/common.runs/*/*_sim_netlist.v -f
	git add ${PROJ_HOME}/xilinx/ip_srcs/${XILINX_PART}/${XILINX_REV}/common/common.srcs/sources_1/ip/*.xci* -f
	git add ${PROJ_HOME}/xilinx/ip_srcs/${XILINX_PART}/${XILINX_REV}/common/common.xpr -f
# 	git add ${PROJ_HOME}/xilinx/ip_srcs/${XILINX_PART}/${XILINX_REV}/device/device.ip_user_files/ip/*/*_sim_netlist.v -f --ignore-errors
# 	git add ${PROJ_HOME}/xilinx/ip_srcs/${XILINX_PART}/${XILINX_REV}/device/device.gen/sources_1/ip/*/*_sim_netlist.v -f
	git add ${PROJ_HOME}/xilinx/ip_srcs/${XILINX_PART}/${XILINX_REV}/device/device.runs/*/*_sim_netlist.v -f
	git add ${PROJ_HOME}/xilinx/ip_srcs/${XILINX_PART}/${XILINX_REV}/device/device.srcs/sources_1/ip/*.xci* -f
# 	git add ${PROJ_HOME}/xilinx/ip_srcs/${XILINX_PART}/${XILINX_REV}/device/device.srcs/sources_1/ip/*.prj -f
	git add ${PROJ_HOME}/xilinx/ip_srcs/${XILINX_PART}/${XILINX_REV}/device/device.xpr -f
# 	git add ${PROJ_HOME}/xilinx/ip_srcs/${XILINX_PART}/${XILINX_REV}/video/video.ip_user_files/ip/*/*_sim_netlist.v -f --ignore-errors
# 	git add ${PROJ_HOME}/xilinx/ip_srcs/${XILINX_PART}/${XILINX_REV}/video/video.runs/*/*_sim_netlist.v -f --ignore-errors
# 	git add ${PROJ_HOME}/xilinx/ip_srcs/${XILINX_PART}/${XILINX_REV}/video/video.srcs/sources_1/ip/*.xcix -f --ignore-errors
# 	git add ${PROJ_HOME}/xilinx/ip_srcs/${XILINX_PART}/${XILINX_REV}/video/video.xpr -f --ignore-errors
