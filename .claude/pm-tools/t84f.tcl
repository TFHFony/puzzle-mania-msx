# frames during one piece move: busy level, samples, skipped, queue
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
set ::H {}
set ::on 0
debug set_watchpoint write_mem 0xC0FC {} { if {$::on} { lappend ::H "[format %.4f [machine_info time]] busy=[peek 0xC148] n=[peek 0xC0FD] sk=[peek 0xC142] qn=[peek 0xC15B] hint=[peek 0xC1EB] pk8=[peek 0xC0E0]" } }
dstep {[peek 0xC00F] == 50} { }
dpause 5.5
dstep 1 { key 8 0x01 0.2 }
dpause 3.5
dstep 1 { key 8 0x01 0.2 }
dpause 3
dstep 1 { key 8 0x80 0.15 }
dpause 0.5
dstep 1 { key 8 0x01 0.2 }
dstep {[peek 0xC0D1] == 1 && [peek 0xC0DF] == 0 && [peek 0xC024] == 16} { }
dpause 3
dstep 1 { set ::on 1; set ::t0 [machine_info time]; key 8 0x20 0.12 }
dpause 1.5
dstep 1 { set ::on 0; set f [open "F:/MSX Projects/PMdev26/work/k84.txt" w]; puts $f "$::t0"; puts $f [join $::H "\n"]; close $f; exit }
drun
