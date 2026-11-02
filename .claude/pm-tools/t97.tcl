# NEO16 banks above 4 MB / 64 MB: during the clip of an attract run, the bank in the window (vbank) against the ROM file
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
set ::res {}
proc chk {} {
  set vb [expr {[peek 0xC040] + 256 * [peek 0xC041]}]
  set s ""
  foreach o {0 1 100 5000 9000 12000} { append s [peek [expr {0x8000+$o}]] " " }
  lappend ::res "vbank=$vb $s"
}
dstep {[peek 0xC00F] == 50} { }
dpause 6
dstep 1 { key 8 0x01 0.2 }
dstep {[peek 0xC1F7] == 1} { poke 0xC000 8; poke 0xC002 8 }
dstep {[peek 0xC0D1] == 255 && [peek 0xC1F7] == 1 && [peek 0xC0D0] == 0 && [expr {[peek 0xC040] + 256 * [peek 0xC041]}] > 300} { }
for {set i 0} {$i < 12} {incr i} {
  dpause 1.7
  dstep 1 { chk }
}
dstep 1 { set fh [open "F:/MSX Projects/PMdev26/work/shots/hb.txt" w]; puts $fh [join $::res "\n"]; close $fh; exit }
drun
