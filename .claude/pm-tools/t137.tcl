# records the audio from the start until the clip begins (attract mode): music level versus the win jingle
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
set ::rec 0
proc w137 {} {
  set vl [expr {[peek 0xC042] + 256*[peek 0xC043]}]
  if {[peek 0xC1F7] == 1 && $vl > 0 && $vl < 2000} { log "clip starts"; record stop; exit }
  after time 0.1 w137
}
dpause 1
dstep 1 { record start "$::env(DUMP).wav" -audioonly; log "rec" }
dstep 1 { key 8 0x01 0.2 }
dstep {[peek 0xC1F7] == 1} { log "attract" }
drun
w137
after time 400 { record stop; exit }
