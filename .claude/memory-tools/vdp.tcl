set throttle off
set ::fh [open $::env(OUT) w]
proc lg {m} { puts $::fh "[format %.2f [machine_info time]] $m"; flush $::fh }
set ::reached 0
debug set_bp 0x$::env(ML) {} { if {!$::reached} { set ::reached 1; lg "mode_loop"; after time 1.0 snap } }
proc skip {} { if {!$::reached} { keymatrixdown 8 1; after time 0.1 { keymatrixup 8 1 }; after time 0.7 skip } }
skip
set ::n 0
proc snap {} {
  incr ::n
  lg "PC=[format %04X [reg PC]] SP=[format %04X [reg SP]] R1=[format %02X [vdpreg 1]] R7=[format %02X [vdpreg 7]] R8=[format %02X [vdpreg 8]] col(icon)=[format %02X [vpeek [expr {0x2000 + 8*256 + 6*8}]]] pat=[format %02X [vpeek [expr {8*256 + 6*8}]]]"
  if {$::n == 1} { set ::throttle on; after time 0.8 shotn }
  if {$::n < 8} { after time 0.15 snap }
}
proc shotn { } { screenshot "$::env(OUT).png"; lg shot; set ::throttle off }
after time 40 { lg done; close $::fh; exit }
