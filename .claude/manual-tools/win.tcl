# the solved screens and the reward film (attract mode plays by itself): env ML, WIN (win_go), OUT, END
set throttle off
set ::choice 0
set ::n 0
proc key {row mask} { keymatrixdown $row $mask; after time 0.12 [list keymatrixup $row $mask] }
proc skip {} { if {!$::choice} { key 8 1; after time 0.7 skip } }
proc shot {n} { set ::throttle on; after time 0.6 [list shot2 $n] }
proc shot2 {n} { screenshot "$::env(OUT)_$n.png"; set ::throttle off }
debug set_bp 0x$::env(ML) {} { set ::choice 1 }
debug set_bp 0x$::env(WIN) {} { incr ::n; set k $::n; after time 4 [list shot w${k}_4]; after time 16 [list shot w${k}_16]; after time 26 [list shot w${k}_26] }
skip
after time $::env(END) { exit }
