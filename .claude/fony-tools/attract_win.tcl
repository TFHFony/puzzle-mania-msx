# boot, attract mode on photo PHOTO (3x3), logs the music events, records the audio (AVI) until 6 s after the win jingle started
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
set ::lt ""
proc ev {} {
  set s "trk=[peek 0xC0D1] on=[peek 0xC0D0] gs=[peek 0xC0DF] att=[peek 0xC1F7] done=[peek 0xC0E7]"
  if {$s ne $::lt} { set ::lt $s; log $s }
  after time 0.02 ev
}

after time 1500 { exit }
dstep {[peek 0xC00F] == 50 || [peek 0xC00F] == 60} { set ph 9; if {[info exists ::env(PHOTO)]} {set ph $::env(PHOTO)}; for {set i 0} {$i < 10} {incr i} {poke [expr 0xC300 + $i] [expr {$i != $ph}]}; record start $::env(REC); log "recording"; ev }
dstep {[peek 0xC1F7] == 1} { poke 0xC380 3; log "attract on" }
dstep {[peek 0xC0D1] == 3 && [peek 0xC0D0] == 1} { log "win jingle started" }
dpause 6
dstep 1 { record stop; log "stopped"; exit }
drun
