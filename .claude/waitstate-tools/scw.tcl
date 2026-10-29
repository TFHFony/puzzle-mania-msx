# SCC title video: time and PC of the frequency writes (9880h) in the middle of a frame, MODE=machine
if {[info exists ::env(FORCE)]} { after time 7 { poke 0xC391 $::env(FORCE) } }
set throttle off
set ::L {}
set ::on 0
set ::cnt 0
debug set_watchpoint write_mem 0x9880 {} { if {$::on} { lappend ::L "[format %.7f [machine_info time]] [format %04X [reg PC]]"; incr ::cnt; if {$::cnt >= 4000} { set fh [open $::env(OUT) w]; puts $fh [join $::L "\n"]; close $fh; exit } } }
after time $::env(TON) { set ::on 1 }
after time 150 { exit }
