# frame periods during the attract mode puzzle
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
set ::H {}
set ::on 0
set ::last 0
debug set_watchpoint write_mem 0xC0FC {} { if {$::on} { set t [machine_info time]; lappend ::H "[format %.4f [expr {$t-$::last}]]:[peek 0xC148]:[peek 0xC0FD]:[peek 0xC0F0]"; set ::last $t } }
dstep {[peek 0xC00F] == 50} { }
dpause 8
dstep 1 { key 8 0x01 0.2 }
dstep {[peek 0xC1F7] == 1 && [peek 0xC0F0] >= 20} { set ::on 1 }
dstep {[peek 0xC0F0] >= 70} { set ::on 0; set f [open "F:/MSX Projects/PMdev26/work/shots/t91.txt" w]; puts $f $::H; close $f; exit }
drun
