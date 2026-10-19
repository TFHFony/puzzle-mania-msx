# frame period per busy level (FREE build), many kinds of action in the puzzle
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
set ::H {}
set ::on 0
debug set_watchpoint write_mem 0xC0FC {} { if {$::on} { lappend ::H "[format %.4f [machine_info time]] [peek 0xC148] [peek 0xC0FD]" } }
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
dstep 1 { set ::on 1 }
dpause 2
for {set i 0} {$i < 6} {incr i} {
  dstep 1 { key 8 0x20 0.12 }
  dpause 0.6
  dstep 1 { key 8 0x80 0.12 }
  dpause 0.6
}
dstep 1 { keymatrixdown 8 0x40 }
dpause 1.6
dstep 1 { keymatrixup 8 0x40 }
dpause 1
dstep 1 { keymatrixdown 4 0x08 }
dpause 1.2
dstep 1 { keymatrixup 4 0x08 }
dpause 1
dstep 1 { key 5 0x02 0.15 }
dpause 2
dstep 1 { key 3 0x01 0.15 }
dpause 1.2
for {set i 0} {$i < 6} {incr i} {
  dstep 1 { key 8 0x20 0.12 }
  dpause 0.3
  dstep 1 { key 8 0x80 0.12 }
  dpause 0.3
}
dstep 1 { keymatrixdown 8 0x40 }
dpause 1.6
dstep 1 { keymatrixup 8 0x40 }
dpause 1
dstep 1 { keymatrixdown 3 0x20 }
dpause 1
dstep 1 { keymatrixup 3 0x20 }
dpause 1
dstep 1 { set ::on 0; set f [open "F:/MSX Projects/PMdev26/work/lev.txt" w]; puts $f [join $::H "\n"]; close $f; exit }
drun
