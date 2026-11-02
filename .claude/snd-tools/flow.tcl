# the start of the game: time of the jingle (entry / return of the stub) and screenshots of the logo
set throttle [expr {[info exists ::env(THR)] ? "on" : "off"}]
set ::L {}
set ::k 0
proc lg {m} { lappend ::L "[format %.3f [machine_info time]] $m" }
proc per {} { screenshot "$::env(OUT)/p[format %02d $::k].png"; incr ::k; after time $::env(PER) per }
after time $::env(T0) per
after time $::env(END) { set f [open "$::env(OUT)/log.txt" w]; puts $f [join $::L "\n"]; close $f; exit }
debug set_bp 0x$::env(STUB) {} { lg "jingle start C=[format %02X [reg C]]" }
debug set_bp 0x$::env(STUBRET) {} { lg "jingle end carry=[expr {[reg AF] & 1}]" }
