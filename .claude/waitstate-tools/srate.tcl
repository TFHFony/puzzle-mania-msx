set throttle off
set ::n 0
set ::go 0
after time $::env(T0) { set ::go 1; set ::t0 [machine_info time] }
after time [expr {$::env(T0) + 4}] { set f [open $::env(OUT) w]; puts $f "$::n [expr {[machine_info time] - $::t0}]"; close $f; exit }
debug set_watchpoint write_io 0xA1 {} { if {$::go} { incr ::n } }
