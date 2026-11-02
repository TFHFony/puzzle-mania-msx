source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
set ::o {}
proc w {} { lappend ::o "[format %.3f [machine_info time]] [expr {[peek 0xC0D2]+256*[peek 0xC0D3]}] [expr {[peek 0xC0D4]+256*[peek 0xC0D5]}] [peek 0xC009] [peek 0xC0D1] [peek 0xC0DF]"; after time 0.5 w }
dstep {[peek 0xC00F] == 50} { }
dpause 6
dstep 1 { key 8 0x01 0.2 }
dpause 3
dstep 1 { key 8 0x01 0.2 }
dpause 3
dstep 1 { key 8 0x01 0.2 }
dstep {[peek 0xC0D0] == 1 && [peek 0xC0D1] == 1 && [peek 0xC0DF] == 0} { w }
dpause 5
dstep 1 { set fh [open "F:/MSX Projects/PMdev26/work/shots/t121.txt" w]; puts $fh [join $::o "\n"]; close $fh; exit }
drun
after time 80 { exit }
