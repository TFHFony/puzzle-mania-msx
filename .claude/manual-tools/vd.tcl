# dump the pattern + colour tables 3 s after every entry of the photo title (title.photo) and every call of memory_att / puzzle
set throttle off
set ::choice 0
set ::k 0
proc key {row mask} { keymatrixdown $row $mask; after time 0.12 [list keymatrixup $row $mask] }
proc skip {} { if {!$::choice} { key 8 1; after time 0.7 skip } }
set ::fh [open $::env(OUT) w]
proc lg {m} { puts $::fh "[format %.2f [machine_info time]] $m"; flush $::fh }
proc dump {n} {
  set f [open "$::env(OUT).$n.bin" wb]
  set d {}
  for {set a 0} {$a < 0x1800} {incr a} { lappend d [vpeek $a] }
  for {set a 0x2000} {$a < 0x3800} {incr a} { lappend d [vpeek $a] }
  puts -nonewline $f [binary format c* $d]
  close $f
  lg "dumped $n"
}
debug set_bp 0x$::env(ML) {} { set ::choice 1 }
debug set_bp 0x$::env(TP) {} { incr ::k; set n $::k; lg "title.photo #$n (last: $::last)"; after time 3 [list dump $n] }
debug set_bp 0x$::env(MA) {} { set ::last memory }
debug set_bp 0x$::env(PZ) {} { set ::last sliding }
set ::last none
skip
after time $::env(END) { lg " end"; close $::fh; exit }
