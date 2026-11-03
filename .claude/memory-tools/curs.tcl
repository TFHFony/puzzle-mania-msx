# the cursor on the choice screen must be there without a key: screenshot 1 s after the choice screen is reached
set throttle off
set ::fh [open $::env(OUT) w]
set ::reached 0
debug set_bp 0x$::env(ML) {} { if {!$::reached} { set ::reached 1; puts $::fh "choice [format %.2f [machine_info time]]"; flush $::fh; after time 1.5 { set ::throttle on; after time 0.6 { screenshot "$::env(OUT).png"; puts $::fh "sprite0 y=[vpeek 0x1B00] x=[vpeek 0x1B01] col=[vpeek 0x1B03]"; puts $::fh " end"; close $::fh; exit } } } }
proc skip {} { if {!$::reached} { keymatrixdown 8 1; after time 0.1 { keymatrixup 8 1 }; after time 0.7 skip } }
skip
