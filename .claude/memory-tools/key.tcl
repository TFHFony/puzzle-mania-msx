set throttle off
set ::fh [open $::env(OUT) w]
proc lg {m} { puts $::fh "[format %.3f [machine_info time]] $m"; flush $::fh }
set ::reached 0
debug set_bp 0x$::env(ML) {} { if {!$::reached} { set ::reached 1; after time 0.5 choose } }
proc skip {} { if {!$::reached} { keymatrixdown 8 1; after time 0.1 { keymatrixup 8 1 }; after time 0.7 skip } }
skip
proc choose {} { keymatrixdown 8 128; after time 0.1 { keymatrixup 8 128 }; after time 0.4 { keymatrixdown 8 1; after time 0.1 { keymatrixup 8 1 }; after time 2.5 test1 } }
proc test1 {} {
  # one RIGHT press of 0.07 s, sample cx / m_prev / k8 every 0.01 s
  lg "start cx=[peek 0xC128] mode?"
  keymatrixdown 8 128
  after time 0.07 { keymatrixup 8 128 }
  set ::t 0; poll
}
proc poll {} { incr ::t; lg "cx=[peek 0xC128] prev=[format %02X [peek 0xC130]] rep=[peek 0xC131]"; if {$::t < 40} { after time 0.01 poll } else { close $::fh; exit } }
after time 100 { close $::fh; exit }
