# attract mode: wait time in the menu, music during the attract puzzle, jingle, clip, back to the menu
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
proc w94 {} {
  set s "size=[peek 0xC001] att=[peek 0xC1F7] trk=[peek 0xC0D1] on=[peek 0xC0D0] gs=[peek 0xC0DF] gt=[peek 0xC0E4] idle=[expr {[peek 0xC1F2]>0}]"
  if {![info exists ::lw] || $s ne $::lw} { log $s; set ::lw $s }
  after time 0.1 w94
}
w94
dstep {[peek 0xC00F] == 50} { }
dpause 8
dstep 1 { key 8 0x01 0.2; log "SPACE pressed" }
dstep {[peek 0xC1F7] == 1 && [peek 0xC0F0] >= 40} { log "puzzle" }
dstep {[peek 0xC1F7] == 0} { log "back"; exit }
drun
