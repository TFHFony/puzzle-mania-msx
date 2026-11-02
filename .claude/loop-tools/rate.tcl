set throttle off
if {[info exists ::env(ZF)]} { set z80_freq_locked false; set z80_freq $::env(ZF) }
set ::n 0; set ::L {}
debug set_watchpoint write_io 0xA0 {} { if {$::wp_last_value == 8} { incr ::n } }
proc tick {} { lappend ::L "[format %.1f [machine_info time]]:$::n"; set ::n 0; after time 0.5 tick }
after time 8 tick
after time 30 { set f [open "$::env(OUT)" w]; puts $f "[join $::L { }]"; close $f; exit }
