set throttle off
set frameskip 0
proc lg {m} { set f [open $::env(LOG) a]; puts $f "[format %.3f [machine_info time]] $m"; close $f }
lg "start"
after time 1 { record start $::env(WAV); lg "recording" }
debug set_bp $::env(ADDR) {} { lg "title video start" }
set ::lastS ""
proc watch {} {
  set s "trk=[peek 0xC0D1] gs=[peek 0xC0DF] gt=[peek 0xC0E4] on=[peek 0xC0D0]"
  if {$s ne $::lastS} { lg $s; set ::lastS $s }
  if {[machine_info time] > 58} { record stop; lg "stopped"; exit }
  after time 0.02 watch
}
after time 0.1 watch
