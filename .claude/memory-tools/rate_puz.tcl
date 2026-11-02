# music samples per second on the memory board when nothing happens: count the PSG data writes (3 per sample) over 5 s
set throttle off
set ::fh [open $::env(OUT) w]
proc lg {m} { puts $::fh "[format %.2f [machine_info time]] $m"; flush $::fh }
set ::reached 0
set ::cnt 0
set ::on 0
debug set_watchpoint write_io 0xA1 {} { if {$::on} { incr ::cnt } }
debug set_bp 0x$::env(ML) {} { if {!$::reached} { set ::reached 1; after time 2.5 { press 1; after time 6 { press 1; after time 8 { press 1; after time 14 count } } } } }
proc press {m} { keymatrixdown 8 $m; after time 0.1 "keymatrixup 8 $m" }
proc skip {} { if {!$::reached} { keymatrixdown 8 1; after time 0.1 { keymatrixup 8 1 }; after time 0.7 skip } }
skip
proc count {} { set ::cnt 0; set ::on 1; lg "counting (trk=[peek 0xC0D1] mus_on=[peek 0xC0D0])"; after time 5 done }
proc done {} { set ::on 0; lg "PSG data writes in 5 s: $::cnt = [expr {$::cnt / 3.0 / 5}] samples/s (8026 at best, 7926 with 2 skipped of 160)"; close $::fh; exit }
after time 120 { close $::fh; exit }
