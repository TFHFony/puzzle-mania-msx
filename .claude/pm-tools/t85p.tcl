# music position (stream pointer) against time: idle, then rapid piece moves
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
set ::H {}
set ::on 0
debug set_watchpoint write_mem 0xC0FC {} { if {$::on} { lappend ::H "[format %.4f [machine_info time]] [peek16 0xC0D2] [peek16 0xC0D4] [peek 0xC148]" } }
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
dpause 2.5
dstep 1 { set ::on 1; set ::t0 [machine_info time] }
dpause 4
dstep 1 { set ::t1 [machine_info time] }
for {set i 0} {$i < 20} {incr i} {
  dstep 1 { key 8 0x20 0.12 }
  dpause 0.25
  dstep 1 { key 8 0x80 0.12 }
  dpause 0.25
  dstep 1 { key 8 0x40 0.12 }
  dpause 0.25
  dstep 1 { key 8 0x10 0.12 }
  dpause 0.25
}
dpause 1
dstep 1 { set ::on 0; set f [open "F:/MSX Projects/PMdev26/work/pos.txt" w]; puts $f "$::t0 $::t1"; puts $f [join $::H "\n"]; close $f; exit }
drun
