# boot; from the start of the menu song log the music events; KEYAT=<s after the menu song started> presses cursor-right once (scenario B), none = scenario A
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
set ::lt ""
set ::tm 0
proc ev {} {
  set s "trk=[peek 0xC0D1] on=[peek 0xC0D0] gs=[peek 0xC0DF] att=[peek 0xC1F7] act=[peek 0xC385] wo=[peek 0xC386] bank=[expr {[peek 0xC0D2]+256*[peek 0xC0D3]}] sel=[peek 0xC002]"
  set k "trk=[peek 0xC0D1] gs=[peek 0xC0DF] att=[peek 0xC1F7] act=[peek 0xC385] wo=[peek 0xC386]"
  if {$k ne $::lt} { set ::lt $k; log $s }
  after time 0.02 ev
}
after time 1500 { exit }
dstep {[peek 0xC0D1] == 0 && [peek 0xC0D0] == 1} { set ::tm [machine_info time]; log "menu song started"; ev }
if {[info exists ::env(KEYAT)]} {
  dstep {[machine_info time] >= $::tm + $::env(KEYAT)} { log "key"; key 8 0x80 100 }
}
dstep {[peek 0xC1F7] == 1} { log "attract on" }
dpause 6
dstep 1 { log "end"; exit }
drun
