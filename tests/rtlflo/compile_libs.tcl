set ver $env(XILINX_REV)
set compile_dir "xilinx_lib/${ver}"
file mkdir ${compile_dir}
puts "${compile_dir}"
compile_simlib -simulator modelsim -directory ${compile_dir}
