set throttle off
after time 33 { keymatrixdown 8 0x01 }
after time 34 { keymatrixup 8 0x01 }
after time 38 {
  set s ""
  for {set r 0} {$r < 24} {incr r} { append s [format %s\n [string map {"\0" " "} [debug read_block VRAM [expr {$r*40}] 40]]] }
  set f [open "$::env(OUT)" w]; puts $f $s; close $f; exit }
