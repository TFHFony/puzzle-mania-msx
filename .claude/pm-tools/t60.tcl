# busy / late frames per steady state (the first 1.5 s after a key press are left out)
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
set ::H {}
set ::ph x
debug set_watchpoint write_mem 0xC148 {} { lappend ::H "b $::ph $::wp_last_value" }
debug set_watchpoint write_mem 0xC0FC {} { lappend ::H "s $::ph $::wp_last_value" }
dstep {[peek 0xC00F] == 50} { set ::ph title }
dpause 6
dstep 1 { set ::ph x; key 8 0x01 0.2 }
dpause 1.5
dstep 1 { set ::ph menu }
dpause 3
dstep 1 { set ::ph x; key 8 0x01 0.2 }
dpause 1.5
dstep 1 { set ::ph size }
dpause 2
dstep 1 { set ::ph x; key 8 0x01 0.2 }
dpause 3
dstep 1 { set ::ph puzzle }
dpause 3
dstep 1 { set ::ph x; key 8 0x80 0.2 }
dpause 0.3
dstep 1 { key 8 0x40 0.2 }
dpause 0.3
dstep 1 { key 8 0x80 0.2 }
dpause 0.3
dstep 1 { set ::ph move }
dpause 1.5
dstep 1 { set f [open "F:/MSX Projects/PMdev26/work/k2log.txt" w]; puts $f [join $::H "\n"]; close $f; exit }
drun
