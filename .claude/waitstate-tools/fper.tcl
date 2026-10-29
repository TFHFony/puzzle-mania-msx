# the period of one video frame of the title video: breakpoint at the frame start label (ADDR), times of hits 5..9
set throttle off
set ::n 0
set ::ts {}
after time 7 { poke 0xC391 $::env(FORCE) }
debug set_bp $::env(ADDR) {} { incr ::n; if {$::n >= 5 && $::n <= 9} { lappend ::ts [machine_info time] }; if {$::n == 9} { set f [open $::env(OUT) w]; puts $f $::ts; close $f; exit } }
after time 150 { exit }
