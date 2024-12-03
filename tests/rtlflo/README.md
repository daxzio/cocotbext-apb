# Usage

Before usage, make sure that `pyyaml` is installed into you working version of python, in this case:

    pip install -r requirements.txt

Should be enough

The contents of this directory is to be used in parallel.  First check out the directory, then create a directory in parallel:

    mkdir ../dut001
    cd ../dut001
    
In this directory you need a `Makefile`, to refer back to the flow:

    RTLFLOW_PATH ?= ../rtlflo

    XILINX_REV ?= 2021.1
    XILINX_VIVADO?=/cadtools/redhat8_x86/xilinx/Vivado/2021.2
    include ${RTLFLOW_PATH}/Makefile

(Change the path to reflect the location of your vivado)

And you need a `project_list.yml` file. In this file are all the inputs to the fpga project, `constraints` and `common_files` being the most, `sim_files` and `syn_files` are used when there are separate files required for sim and for synth (In pure synth mode this is redundant).  A `generic` is given as an example, if you are not passing generics, remove:

```
test_top: dut_top
synth_top: dut_top
part: xcku115-flva1517-2-i
libraries:
external_libraries:
constraints_files:
    - ../../constr/timing.xdc
generics:
    G_REVNUM: x"00000ab0"
sim_files:
syn_files:
common_files:
    - ../../xilinx/ip_srcs/${XILINX_PART}/${XILINX_REV}/dut_top/dut_top.srcs/sources_1/ip/clk_wiz.xcix
    - ../../src/and.sv
    - ../../src/dut_top.sv
```

The `part` is the exact part name as used by vivado.

`test_top` is only of real importance if one is using the flow for simulation.

`synth_top` is the top of you synthesised design.

All paths are either relative to the current directory or it can be the explict path on the system.  Relative paths are preferred as they survive many checkouts on different operating systems.  Environment variables can be used to pass in variables to be used in the path info (mainly used for changing parts of vivado version).

For operation you can `make help`

```
help               : List all commands
clean              : Clean up all working file
run <default>      : Compile and run command line all tests
run TEST=testname   Compile and run command line single test

    make run TEST=work.tb_xs.test_004

gui                : Compile and start GUI mode for all tests
gui TEST=testname  Compile and run command line single test

    make gui TEST=work.tb_xs.test_004

license            : Return the status of the license servers
vivado_version     : Return the version of vivado found
vivado_libs        : Compile xilinx libraries under modelsim
vivado_build       : Build the vivado project from scratch
vivado_synth       : Synthesise the vivado project
vivado_run         : Compile and generate the vivado project
vivado             : A vivado_build followed by vivado_run
```

But for initial debug run use `make vivado_build`

You will find a new directory in your current directory, and inside is a `*.xpr` file, open this in vivado.
