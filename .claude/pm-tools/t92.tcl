# time of every PSG sample (write of register 8) during the moves of the attract mode -> work/shots/t92.txt
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
set ::L {}
set ::on 0
debug set_watchpoint write_io 0xA0 {} { if {$::on && $::wp_last_value == 8} { lappend ::L "[format %.6f [machine_info time]] [peek 0xC0F0]" } }
dstep {[peek 0xC00F] == 50} { }
dpause 8
dstep 1 { key 8 0x01 0.2 }
dstep {[peek 0xC1F7] == 1 && [peek 0xC0F0] >= 20} { set ::on 1 }
dstep {[peek 0xC0F0] >= 60} { set ::on 0; set f [open "F:/MSX Projects/PMdev26/work/shots/t92.txt" w]; puts $f [join $::L "\n"]; close $f; exit }
drun
