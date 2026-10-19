# rapid piece moves in a 4x4 puzzle: silent gaps of the music
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
set ::L {}
set ::on 0
debug set_watchpoint write_io 0xA0 {} { if {$::on && $::wp_last_value == 8} { lappend ::L [machine_info time] } }
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
dstep 1 { set ::on 1; set ::t0 [machine_info time] }
for {set i 0} {$i < 24} {incr i} {
  dstep 1 { key 8 0x20 0.12 }
  dpause 0.25
  dstep 1 { key 8 0x80 0.12 }
  dpause 0.25
  dstep 1 { key 8 0x40 0.12 }
  dpause 0.25
  dstep 1 { key 8 0x10 0.12 }
  dpause 0.25
}
dstep 1 { set ::on 0; set f [open "F:/MSX Projects/PMdev26/work/psgm.txt" w]; puts $f "$::t0"; puts $f [join $::L "\n"]; close $f; exit }
drun
