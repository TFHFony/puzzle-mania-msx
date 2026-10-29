set throttle off
set ::go 0
set ::L {}
set ::nf 0
after time $::env(T0) { set ::go 1 }
debug set_bp 0xD300 {} { if {$::go} { incr ::nf; lappend ::L "M [format %.9f [machine_info time]]"; if {$::nf > 3} { set f [open $::env(OUT) w]; puts $f [join $::L "\n"]; close $f; exit } } }
debug set_watchpoint write_mem 0x9880 {} { if {$::go && $::nf > 0} { lappend ::L "W [format %.9f [machine_info time]]" } }
after time 100 { exit }
