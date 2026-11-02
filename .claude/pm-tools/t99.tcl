# the whole cycle without keys: FONY -> title (video) -> menu -> attract -> jingle -> clip -> title (photo) -> menu -> attract -> ...
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
proc w99 {} {
  set s "tit=[peek 0xC1F9] att=[peek 0xC1F7] tv=[expr {[peek 0xC1EF] != 0}] trk=[peek 0xC0D1] on=[peek 0xC0D0] done=[peek 0xC300]"
  if {![info exists ::lw] || $s ne $::lw} { log $s; set ::lw $s }
  after time 0.25 w99
}
w99
after time 520 { exit }
