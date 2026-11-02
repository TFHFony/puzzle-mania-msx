# press a key (env ROW, MASK) 0.5 s after the start of the jingle: how soon does it return (carry)?
set throttle off
set ::L {}
proc lg {m} { lappend ::L "[format %.3f [machine_info time]] $m" }
debug set_bp 0x7F2A {} { reg C 1; lg "jingle start C=[format %02X [reg C]]"; after time $::env(AT) { keymatrixdown $::env(ROW) $::env(MASK); after time 0.15 { keymatrixup $::env(ROW) $::env(MASK) } } }
debug set_bp 0x7F36 {} { lg "jingle end carry=[expr {[reg AF] & 1}]"; set f [open $::env(OUT) w]; puts $f [join $::L "\n"]; close $f; exit }
after time 60 { exit }
