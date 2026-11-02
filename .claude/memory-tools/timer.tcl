# the timer of the sliding puzzle: p_secs against the emulated time (20 s)
set throttle off
set ::fh [open $::env(OUT) w]
proc lg {m} { puts $::fh "[format %.2f [machine_info time]] $m"; flush $::fh }
set ::reached 0
set ::pl 0
debug set_bp 0x$::env(PL) {} { if {!$::pl} { set ::pl 1; lg "puzzle loop starts: p_secs=[expr {[peek 0xC0F2] + 256*[peek 0xC0F3]}]" } }
debug set_bp 0x$::env(ML) {} { if {!$::reached} { set ::reached 1; lg "choice"; after time 0.5 { press 1; after time 1.5 { press 1; after time 1.5 { press 1; after time 4 start } } } } }
proc press {m} { keymatrixdown 8 $m; after time 0.1 "keymatrixup 8 $m" }
proc skip {} { if {!$::reached} { keymatrixdown 8 1; after time 0.1 { keymatrixup 8 1 }; after time 0.7 skip } }
skip
proc secs {} { expr {[peek 0xC0F2] + 256*[peek 0xC0F3]} }
proc start {} { set ::t0 [machine_info time]; set ::s0 [secs]; lg "start p_secs=$::s0"; after time 20 stop }
proc stop {} { lg "after 20 s emulated: p_secs=[secs] (delta [expr {[secs]-$::s0}]) v_hz=[peek 0xC00F]"; close $::fh; exit }
after time 90 { lg timeout; close $::fh; exit }
