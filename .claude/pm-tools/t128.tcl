# attract timing: the menu song ends -> the cursor goes to a photo -> the size menu -> the puzzle
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
proc w {} {
  set s "wr=[peek 0xC381] att=[peek 0xC1F7] sel=[peek 0xC002] win=[peek 0xC066] photo=[peek 0xC000] ssel=[peek 0xC06B] size=[peek 0xC001] trk=[peek 0xC0D1] on=[peek 0xC0D0] hz=[peek 0xC00F] r9=[format %02X [peek 0xFFE8]]"
  if {![info exists ::lw] || $s ne $::lw} { log $s; set ::lw $s }
  after time 0.1 w
}
dstep {[peek 0xC00F] == 50} { w }
dpause 80
dstep 1 { exit }
drun
after time 150 { exit }
