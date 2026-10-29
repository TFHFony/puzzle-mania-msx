set throttle off
set ::lastS ""
proc lg {m} { set f [open $::env(LOG) a]; puts $f "[format %.3f [machine_info time]] $m"; close $f }
proc watch {} {
  set s "on=[peek 0xC0D0] trk=[peek 0xC0D1] gs=[peek 0xC0DF] gt=[peek 0xC0E4] tit=[peek 0xC1F9]"
  if {$s ne $::lastS} { lg $s; set ::lastS $s }
  if {[machine_info time] > 75} { exit }
  after time 0.02 watch
}
after time 0.1 watch
