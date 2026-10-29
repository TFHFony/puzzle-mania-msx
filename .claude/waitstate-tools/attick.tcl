# attract mode audio: records a wav from the start of the attract mode, logs the state changes (time, v_size, mus_on, gain, track) until 4 s after the puzzle starts
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
set ::lastS ""
set ::t0 0
proc lg {m} { set f [open $::env(LOG) a]; puts $f "[format %.3f [machine_info time]] $m"; close $f }
proc watch {} {
  set s "size=[peek 0xC001] on=[peek 0xC0D0] trk=[peek 0xC0D1] gs=[peek 0xC0DF] gt=[peek 0xC0E4] tab=[format %02X [peek 0xC0DE]] att=[peek 0xC1F7] sz=[peek 0xC380]"
  if {$s ne $::lastS} { lg $s; set ::lastS $s }
  after time 0.02 watch
}
after time 900 { exit }
dstep {[peek 0xC00F] == 50 || [peek 0xC00F] == 60} { for {set i 0} {$i < 10} {incr i} {poke [expr 0xC300 + $i] [expr {$i != 9}]}; poke 0xC380 4 }
dstep {[peek 0xC1F7] == 1} { lg "attract on"; record start $::env(WAV); watch }
dstep {[peek 0xC1F7] == 1 && [peek 0xC001] != 0} { set ::t1 [machine_info time]; lg "size chosen" }
dstep {[machine_info time] >= $::t1 + 5} { record stop; lg "stopped"; exit }
drun
