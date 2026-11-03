# music samples per second while the attract bot plays memory: count the PSG data writes (3 per sample) in 3 windows of 6 s after memory_att starts
set throttle off
set ::fh [open $::env(OUT) w]
proc lg {m} { puts $::fh "[format %.2f [machine_info time]] $m"; flush $::fh }
set ::reached 0
set ::choice 0
set ::cnt 0
set ::on 0
set ::k 0
debug set_watchpoint write_io 0xA1 {} { if {$::on} { incr ::cnt } }
debug set_bp 0x$::env(ML) {} { set ::choice 1 }
debug set_bp 0x$::env(MA) {} { if {!$::reached} { set ::reached 1; after time 8 count } }
proc skip {} { if {!$::choice} { keymatrixdown 8 1; after time 0.1 { keymatrixup 8 1 }; after time 0.7 skip } }
skip
proc count {} { set ::cnt 0; set ::on 1; after time 6 done }
proc done {} { set ::on 0; incr ::k; lg "window $::k: [expr {$::cnt / 3.0 / 6}] samples/s (8026 at best)"; if {$::k < 3} { after time 3 count } else { lg " end"; close $::fh; exit } }
after time 400 { close $::fh; exit }
