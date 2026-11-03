set throttle off
set ::choice 0
proc key {row mask} { keymatrixdown $row $mask; after time 0.12 [list keymatrixup $row $mask] }
proc skip {} { if {!$::choice} { key 8 1; after time 0.7 skip } }
set ::fh [open $::env(OUT) w]
proc lg {m} { puts $::fh "[format %.2f [machine_info time]] $m"; flush $::fh }
proc cb {} { set s ""; for {set a 0x3798} {$a < 0x37C0} {incr a} { append s [format %02X [vpeek $a]] }; return $s }
proc st {tag} { lg "cells3798: [cb]"; lg [format "%s: qn=%d go=%d dend=%02X lc=%02X HL2=%04X DE2=%04X BC2=%04X AF2=%04X mus_on=%d" $tag [peek 0xC15B] [peek 0xC15F] [peek 0x$::env(JD)] [peek 0x$::env(JL)] [reg HL2] [reg DE2] [reg BC2] [reg AF2] [peek 0xC0D0]] }
debug set_bp 0x$::env(ML) {} { set ::choice 1 }
debug set_bp 0x$::env(WIN) {} { st "win_go" ; after time 1 {st "win+1"}; after time 5 {st "win+5"} }
debug set_bp 0x$::env(TP) {} { if {$::choice} { st "title.photo" } }
skip
after time $::env(END) { lg " end"; close $::fh; exit }
