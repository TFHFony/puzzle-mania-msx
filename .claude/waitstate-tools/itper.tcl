set throttle off
set ::n 0
set ::ts {}
debug set_bp $::env(ADDR) {} { incr ::n; if {$::n >= 200 && $::n <= 215} { lappend ::ts [machine_info time] }; if {$::n == 215} { set f [open $::env(OUT) w]; puts $f $::ts; close $f; exit } }
after time 150 { exit }
