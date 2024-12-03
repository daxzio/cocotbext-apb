set now [clock seconds]
set timestr [clock format $now -format "%y%m%d"]

set BASE_DIR [pwd]
set BITSTREAM_DIR "${BASE_DIR}/../../../../bitstreams"
file mkdir ${BITSTREAM_DIR}

#set NAME [get_property NAME [current_project]]
set x [lrange [file split $BASE_DIR] end-1 end-1]
regsub ".runs" $x "" NAME
puts $NAME

set bitstream [glob -directory $BASE_DIR {*.bit}]
for {set i 0} {$i < 100} {incr i} {
    set bitfile "${BITSTREAM_DIR}/${NAME}-${timestr}.0${i}.bit"
    if {![file exists $bitfile]} {
        break
    }
}
file copy -force $bitstream $bitfile

regsub ".bit$" $bitfile ".mcs" mcsfile
regsub ".bit$" $bitfile ".prm" prmfile

write_cfgmem -format mcs \
    -force \
    -checksum \
    -interface SPIx4 \
    -size 256 \
    -loadbit "up 0x0 ${bitfile}" \
    -file ${mcsfile}
