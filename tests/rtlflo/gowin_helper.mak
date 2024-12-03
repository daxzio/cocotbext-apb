ifneq ($(GOWIN_SOURCES),)
    COMPILE_LIBS?=../../libs
    CDSLIB?=./cds_${SIM}.lib
    GOWIN_LIBS?=${COMPILE_LIBS}/${SIM}/gowin
    GOWIN_CNT=`grep -s gowin ${CDSLIB} | wc -l`
    COMPILE_ARGS+=-reflib ${GOWIN_LIBS}
endif

gowin_cdslib:
	@if [ "${GOWIN_CNT}" -eq "0" ]; then \
		mkdir -p ${GOWIN_LIBS} ; \
		echo "DEFINE gowin ${GOWIN_LIBS}" >> ${CDSLIB} ; \
	fi

${COMPILE_LIBS}/ius/gowin: ${CDSLIB} gowin_cdslib
	ncvlog -MESSAGES -NOLOG -64bit -CDSLIB ${CDSLIB} -WORK gowin ${RTLFLO_PATH}/gowin/prim_sim.v ${GOWIN_SOURCES}

gowin_ius_lib: | ${GOWIN_LIBS}

gowin_xcelium_lib: | ${GOWIN_LIBS}

gowin_library:
	mkdir -p ${COMPILE_LIBS}
ifeq ($(SIM),ius)
	${MAKE} gowin_ius_lib
else ifeq ($(SIM),xcelium)
	${MAKE} gowin_xcelium_lib
endif

gowin_library_clean:
	@rm -rf ${GOWIN_LIBS}
	@sed -i '/gowin/d' ${CDSLIB} || true

cdslib:: gowin_cdslib

all_libs:: gowin_library

all_libs_clean:: gowin_library_clean
