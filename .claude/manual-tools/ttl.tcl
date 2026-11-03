set throttle off
set ::choice 0
proc key {row mask} { keymatrixdown $row $mask; after time 0.12 [list keymatrixup $row $mask] }
proc skip {} { if {!$::choice} { key 8 1; after time 0.7 skip } }
proc shot {n} { set ::throttle on; after time 0.6 [list shot2 $n] }
proc shot2 {n} { screenshot "$::env(OUT)_$n.png"; set ::throttle off }
debug set_bp 0x$::env(ML) {} { set ::choice 1 }
debug set_bp 0x$::env(WIN) {} { foreach d {18 21 24 27 30 33 36 39 42} { after time $d [list shot t$d] } }
skip
after time $::env(END) { exit }
