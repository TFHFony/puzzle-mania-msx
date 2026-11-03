# the attract mode: wait at the choice screen without a key; log what starts (memory_att, puzzle, win), screenshots
set throttle off
set ::fh [open $::env(OUT) w]
proc lg {m} { puts $::fh "[format %.2f [machine_info time]] $m"; flush $::fh }
set ::reached 0
set ::n 0
debug set_bp 0x$::env(ML) {} { incr ::n; if {!$::reached} { set ::reached 1; lg "choice screen (first)"; after time 1 { shot choice } } else { lg "mode_loop again (hit $::n)" } }
debug set_bp 0x$::env(MA) {} { lg "memory_att: the attract mode plays memory"; after time 8 { shot mem8 }; after time 20 { shot mem20 } }
debug set_bp 0x$::env(PZ) {} { lg "puzzle: the attract mode plays the sliding puzzle" ; after time 8 { shot pz8 } }
debug set_bp 0x$::env(WIN) {} { lg "win_go"; after time 4 { shot w4 }; after time 12 { shot w12 }; after time 30 { shot w30 } }
proc shot {n} { set ::throttle on; after time 0.6 [list shot2 $n] }
proc shot2 {n} { screenshot "$::env(OUT).$n.png"; set ::throttle off; lg "shot $n" }
proc skip {} { if {!$::reached} { keymatrixdown 8 1; after time 0.1 { keymatrixup 8 1 }; after time 0.7 skip } }
skip
after time $::env(END) { lg "end"; close $::fh; exit }
