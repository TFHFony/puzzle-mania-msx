source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
set ::L {}
set ::on 0
debug set_watchpoint write_mem 0x9800 {} { if {$::on} { lappend ::L "[format %.7f [machine_info time]] $::wp_last_value" } }
dstep {[peek 0xC00F] == 50} { }
dpause 9
dstep 1 { set ::on 1 }
dpause 0.5
dstep 1 { set ::on 0; set fh [open "F:/MSX Projects/PMdev26/work/shots/t119.txt" w]; puts $fh [join $::L "\n"]; close $fh; exit }
drun
after time 40 { exit }
