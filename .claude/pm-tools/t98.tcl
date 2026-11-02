# the PSG jingle: every PSG write while the win loop runs (music off) -> work/shots/t98.txt
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
set ::L {}
set ::reg 0
debug set_watchpoint write_io 0xA0 {} { set ::reg $::wp_last_value }
debug set_watchpoint write_io 0xA1 {} { if {[peek 0xC1F7] == 1 && [peek 0xC0D0] == 0 && $::reg < 11} { lappend ::L "[format %.5f [machine_info time]] $::reg $::wp_last_value" } }
dstep {[peek 0xC00F] == 50} { }
dpause 6
dstep 1 { key 8 0x01 0.2 }
dstep {[peek 0xC1F7] == 1} { }
dstep {[peek 0xC1F7] == 1 && [peek 0xC0D0] == 0 && [llength $::L] > 5} { }
dpause 7
dstep 1 { set fh [open "F:/MSX Projects/PMdev26/work/shots/t98.txt" w]; puts $fh [join $::L "\n"]; close $fh; exit }
drun
