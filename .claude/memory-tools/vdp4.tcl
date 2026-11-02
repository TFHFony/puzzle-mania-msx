set throttle off
set ::fh [open $::env(OUT) w]
proc lg {m} { puts $::fh "[format %.4f [machine_info time]] $m"; flush $::fh }
set ::reached 0
set ::ring {}
set ::done 0
debug set_bp 0x$::env(ML) {} { if {!$::reached} { set ::reached 1; lg "mode_loop"; poll } }
debug set_watchpoint write_io {0x98 0x99} {} { if {$::reached} { set ::ring [lrange [concat $::ring [list "[format %02X $::wp_last_address]:[format %02X $::wp_last_value]@[format %04X [reg PC]]"]] end-24 end] } }
proc poll {} {
  if {$::done} { return }
  set r1 [vdpreg 1]
  if {$r1 != 0x40 && $r1 != 0xC0 && $r1 != 0xE0 && $r1 != 0x60} {
    set ::done 1
    lg "R1=[format %02X $r1] regs=[join [lmap a {0 1 2 3 4 5 6 7} {format %02X [vdpreg $a]}] { }] PC=[format %04X [reg PC]]"
    lg "last writes: $::ring"
    close $::fh; exit
  }
  after time 0.0005 poll
}
proc skip {} { if {!$::reached} { keymatrixdown 8 1; after time 0.1 { keymatrixup 8 1 }; after time 0.7 skip } }
skip
after time 14 { lg "no change"; close $::fh; exit }
