# SCC volume / enable writes and any non-zero PSG volume write during the menu music and the attract puzzle
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
set ::L {}
set ::psgnz 0
set ::reg 0
debug set_watchpoint write_mem {0x988A 0x988F} {} { lappend ::L "[format %.2f [machine_info time]] [format %04X $::wp_last_address]=$::wp_last_value" }
debug set_watchpoint write_io 0xA0 {} { set ::reg $::wp_last_value }
debug set_watchpoint write_io 0xA1 {} { if {$::reg >= 8 && $::reg <= 10 && $::wp_last_value != 0 && [peek 0xC1F7] == 0} { incr ::psgnz } }
dstep {[peek 0xC00F] == 50} { }
dpause 6
dstep 1 { key 8 0x01 0.2 }
dstep {[peek 0xC1F7] == 1} { }
dstep {[peek 0xC1F7] == 0} { set fh [open "F:/MSX Projects/PMdev26/work/shots/t103.txt" w]; puts $fh "psg nonzero volume writes (outside the jingle): $::psgnz"; puts $fh [join $::L "\n"]; close $fh; exit }
drun
