etana:
	peakrdl etana regblock.rdl -o ./ --cpuif ${CPUIF} ${RDL_ARGS} --rename regblock

regblock:
	peakrdl regblock regblock.rdl -o ./ --cpuif ${CPUIF} --err-if-bad-addr --err-if-bad-rw --rename regblock
