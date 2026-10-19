# sprite cursor control (C): moving the cursor must not make action frames (level 2 -> K 10); SPACE slides (level 2)
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
set ::H {}
set ::go 0
debug set_watchpoint write_mem 0xC148 {} { if {$::go} { lappend ::H "b $::wp_last_value [format %.3f [machine_info time]]" } }
debug set_watchpoint write_mem 0xC0FC {} { if {$::go} { lappend ::H "s $::wp_last_value [format %.3f [machine_info time]]" } }
dstep {[peek 0xC00F] == 50} { }
dpause 6
dstep 1 { key 8 0x01 0.2 }
dpause 4
dstep 1 { key 8 0x01 0.2 }
dpause 3
dstep 1 { key 8 0x01 0.2 }
dpause 4
dstep 1 { key 3 0x01 0.15 }
dpause 1
dstep 1 { set ::go 1; log "ctl=[peek 0xC01A]"; key 8 0x80 0.1 }
dpause 0.5
dstep 1 { key 8 0x40 0.1 }
dpause 0.5
dstep 1 { key 8 0x10 1.0 }
dpause 1.5
dstep 1 { key 8 0x01 0.15 }
dpause 1.5
dstep 1 { set f [open "F:/MSX Projects/PMdev26/work/k2log.txt" w]; puts $f [join $::H "\n"]; close $f; log "moves=[peek 0xC0F0]"; exit }
drun
