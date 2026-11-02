set throttle off
set ::L {}
debug set_bp 0x000049A2 {} { lappend ::L "wipe_clear start [format %.3f [machine_info time]]" }
debug set_bp 0x4999 {} { lappend ::L "wipe_clear end [format %.3f [machine_info time]]" }
after time 9 { set f [open $::env(OUT) w]; puts $f [join $::L "\n"]; close $f; exit }
