set throttle off
if {[info exists ::env(ZF)]} { set z80_freq_locked false; set z80_freq $::env(ZF) }
after time $::env(AT) {
  set s ""
  for {set r 0} {$r < 24} {incr r} { append s [format %s\n [string map {"\0" " "} [debug read_block VRAM [expr {$r*40}] 40]]] }
  set f [open $::env(OUT) w]; puts $f $s; close $f
  exit }
