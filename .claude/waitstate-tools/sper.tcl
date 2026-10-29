# times of the PSG data writes (A1h) of 2 consecutive frames of the idle menu, from the first mvsync_ call after T0
set throttle off
set ::go 0
set ::L {}
after time $::env(T0) { set ::go 1 }
debug set_bp 0xD300 {} { if {$::go} { incr ::go; lappend ::L "M [format %.7f [machine_info time]]"; if {$::go > 3} { set f [open $::env(OUT) w]; puts $f [join $::L "\n"]; close $f; exit } } }
debug set_watchpoint write_io 0xA1 {} { if {$::go > 1} { lappend ::L "W [format %.7f [machine_info time]]" } }
after time 100 { exit }
