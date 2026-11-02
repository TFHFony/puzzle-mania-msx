set throttle off
set ::fh [open $::env(OUT) w]
proc lg {m} { puts $::fh "[format %.2f [machine_info time]] $m"; flush $::fh }
set ::reached 0
debug set_bp 0x$::env(ML) {} { if {!$::reached} { set ::reached 1; foreach d {1.5 3 5} { after time $d [list snapm $d] } } }
proc snapm {d} { lg "after $d s: mus_on=[peek 0xC0D0] trk=[peek 0xC0D1] gain_step=[peek 0xC0DF] mus_ptr=[format %04X [expr {[peek 0xC0DC] + 256*[peek 0xC0DD]}]]" }
proc skip {} { if {!$::reached} { keymatrixdown 8 1; after time 0.1 { keymatrixup 8 1 }; after time 0.7 skip } }
skip
after time 30 { close $::fh; exit }
