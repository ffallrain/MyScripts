#!/bin/sh 
#\
exec csts -f "$0" ${1+"$@"} 

set infile [lindex $argv 0]

prop setparam E_SCREEN extended 0
set record 0

set fh [molfile open $infile r hydrogens add]


molfile loop $fh ehandle {
	incr record
	#if {$record> 10} break
	set screen [ens get $ehandle E_SCREEN]
	set nsc [ens get $ehandle E_NAME]
	puts [format "%s\t%s" $nsc $screen]	 
	
}

