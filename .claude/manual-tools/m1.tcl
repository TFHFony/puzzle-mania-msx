# MSX1 / MSX2 comparison: the photo menu choice, the 3x3 puzzle
set throttle off
set ::choice 0
proc key {row mask} { keymatrixdown $row $mask; after time 0.12 [list keymatrixup $row $mask] }
proc skip {} { if {!$::choice} { key 8 1; after time 0.7 skip } }
proc shot {n} { set ::throttle on; after time 0.6 [list shot2 $n] }
proc shot2 {n} { screenshot "$::env(OUT)_$n.png"; set ::throttle off }
debug set_bp 0x$::env(ML) {} { if {!$::choice} { set ::choice 1
  after time 3 { key 8 1 }; after time 7 { shot photomenu }; after time 8 { key 8 1 }; after time 11 { key 8 1 }; after time 18 { shot puzzle }; after time 20 { exit } } }
skip
after time 200 { exit }
