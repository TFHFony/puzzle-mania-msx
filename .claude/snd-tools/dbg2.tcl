set throttle off
set ::fh [open $::env(OUT) w]
proc lg {m} { puts $::fh "[format %.3f [machine_info time]] $m PC=[format %04X [reg PC]] SP=[format %04X [reg SP]] A=[format %02X [reg A]]"; flush $::fh }
foreach a $::env(BPS) { debug set_bp 0x$a {} "lg bp$a" }
debug set_condition {[reg PC] == 0x0000 && [machine_info time] > 0.3} { lg RESET }
after time $::env(SEC) { lg end; close $::fh; exit }
