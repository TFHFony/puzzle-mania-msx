set throttle off
set ::fh [open $::env(OUT) w]
proc lg {m} { puts $::fh "[format %.3f [machine_info time]] $m"; flush $::fh }
set ::reached 0
set ::cnt 0
debug set_bp 0x$::env(ML) {} { if {!$::reached} { set ::reached 1; lg "mode_loop" } }
debug set_watchpoint write_io 0x99 {} { if {$::reached && $::cnt < 400} { incr ::cnt; lg "w99 val=[format %02X $::wp_last_value] PC=[format %04X [reg PC]]" } }
proc skip {} { if {!$::reached} { keymatrixdown 8 1; after time 0.1 { keymatrixup 8 1 }; after time 0.7 skip } }
skip
after time 12 { lg done; close $::fh; exit }
