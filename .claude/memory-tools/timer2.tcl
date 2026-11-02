set throttle off
set ::fh [open $::env(OUT) w]
proc lg {m} { puts $::fh "[format %.2f [machine_info time]] $m"; flush $::fh }
set ::reached 0
debug set_bp 0x$::env(ML) {} { if {!$::reached} { set ::reached 1; lg "choice"; after time 0.5 { lg "SPACE 1 (sliding)"; press 1; after time 4 { lg "SPACE 2 (photo)"; press 1; after time 6 { lg "SPACE 3 (size)"; press 1; poll } } } } }
proc press {m} { keymatrixdown 8 $m; after time 0.1 "keymatrixup 8 $m" }
proc skip {} { if {!$::reached} { keymatrixdown 8 1; after time 0.1 { keymatrixup 8 1 }; after time 0.7 skip } }
skip
proc secs {} { expr {[peek 0xC0F2] + 256*[peek 0xC0F3]} }
set ::seen 0
set ::last -9
proc poll {} {
  set on [peek 0xC0D0]; set trk [peek 0xC0D1]; set s [secs]
  if {$trk != $::last} { set ::last $trk; lg "trk=$trk mus_on=$on p_secs=$s" }
  if {$trk == 1 && $s < 4} { lg "puzzle running: p_secs=$s" }
  if {[machine_info time] < 70} { after time 0.25 poll } else { close $::fh; exit }
}
after time 60 { close $::fh; exit }
