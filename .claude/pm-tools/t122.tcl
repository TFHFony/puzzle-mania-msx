# the SCC title video: time and PC of every frequency write (9880h) while the video plays
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
set ::L {}
set ::on 0
debug set_watchpoint write_mem 0x9880 {} { if {$::on} { lappend ::L "[format %.7f [machine_info time]] [format %04X [reg PC]]" } }
dstep {[peek 0xC00F] == 50} { }
dstep {[peek 0xC1EF] >= 1 && [peek 0xC1EF] != 255} { set ::on 1 }
dpause 1.5
dstep 1 { set ::on 0; set fh [open "F:/MSX Projects/PMdev26/work/shots/t122.txt" w]; puts $fh [join $::L "\n"]; close $fh; exit }
drun
after time 45 { exit }
