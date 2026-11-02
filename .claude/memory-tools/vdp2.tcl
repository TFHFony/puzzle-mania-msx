set throttle off
set ::fh [open $::env(OUT) w]
foreach t {7 8.0 8.7} { after time $t [list apply {{} { puts $::fh "[format %.2f [machine_info time]] regs=[join [lmap a {0 1 2 3 4 5 6 7 8} {format %02X [vdpreg $a]}] { }] PC=[format %04X [reg PC]]"; flush $::fh }}] }
after time 12 { close $::fh; exit }
