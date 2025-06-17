# vivado -mode batch -source ../../../../rtlflo/migrate.tcl

set version [version -short]
set year [lindex [split $version "."] 0]
set project "device"
# set project "common"
# set part "xc7a100tcsg324-1"
# set part "xc7k325tffg900-2"
set part "xc7a35tcpg236-1"

open_project "${project}/${project}.xpr"
set_property part ${part} [current_project]
config_ip_cache -clear_output_repo
# report_ip_status -name ip_status
upgrade_ip [get_ips]
# set_property coreContainer.enable 1 [current_project]

set xcis [get_files *.xci*]
reset_target all ${xcis}
export_ip_user_files -of_objects [get_files ${xcis}] -sync -no_script -force -quiet

foreach xci $xcis {
    create_ip_run -quiet -force [get_files -of_objects [get_fileset sources_1] $xci]
}

# set ips [get_ips *]
# foreach ip $ips {
#     delete_ip_run [get_ips ${ip}]
# }

# set ips [get_ips *]
# foreach ip $ips {
#     puts $ip
#     set xci [get_files */$ip.xci*]
#     puts $xci
# #     reset_target all [get_files $xci]
# #     export_ip_user_files -of_objects [get_files $xci] -sync -no_script -force -quiet
#     foreach x $xci {
#         create_ip_run -quiet -force [get_files -of_objects [get_fileset sources_1] $x]
#     }
# }
puts $year
if {$year == 2021} {
    set_property flow {Vivado Synthesis 2021} [get_runs *synth*]
    set_property flow {Vivado Implementation 2021} [get_runs *impl*]
} else {
    set_property flow {Vivado Synthesis 2024} [get_runs *synth*]
    set_property flow {Vivado Implementation 2024} [get_runs *impl*]
}
set runs [get_runs *_synth*]
launch_runs $runs -jobs 24
wait_on_runs $runs
close_project
