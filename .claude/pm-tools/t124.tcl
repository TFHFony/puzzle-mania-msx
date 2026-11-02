# music speed: menu music (track 0) or puzzle music (track 1); env TRK
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle on
set trk $::env(TRK)
dstep {[peek 0xC00F] == 50} { }
dpause 6
dstep 1 { key 8 0x01 0.2 }
if {$trk == 1} {
  dpause 3
  dstep 1 { key 8 0x01 0.2 }
  dpause 3
  dstep 1 { key 8 0x01 0.2 }
}
dstep {[peek 0xC0D0] == 1 && [peek 0xC0D1] == $trk && [peek 0xC1F7] == 0} { record start -audioonly "F:/MSX Projects/PMdev26/work/shots/rec.wav" }
dpause 9
dstep 1 { record stop; exit }
drun
after time 80 { exit }
