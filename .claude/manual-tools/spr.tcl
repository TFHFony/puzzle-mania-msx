# dump the sprite attribute table + VDP regs on the title screen after the memory attract win
set throttle off
set ::choice 0
proc key {row mask} { keymatrixdown $row $mask; after time 0.12 [list keymatrixup $row $mask] }
proc skip {} { if {!$::choice} { key 8 1; after time 0.7 skip } }
set ::fh [open $::env(OUT) w]
proc dump {tag} {
  puts $::fh "== $tag t=[format %.1f [machine_info time]] R1=[format %02X [vdpreg 1]] R6=[format %02X [vdpreg 6]]"
  set s ""
  for {set i 0} {$i < 32} {incr i} { set y [vpeek [expr {0x1B00+4*$i}]]; append s [format "%d:%02X,%02X,%02X,%02X " $i $y [vpeek [expr {0x1B01+4*$i}]] [vpeek [expr {0x1B02+4*$i}]] [vpeek [expr {0x1B03+4*$i}]]]; if {$y == 0xD0} { break } }
  puts $::fh $s; flush $::fh
}
debug set_bp 0x$::env(ML) {} { set ::choice 1 }
debug set_bp 0x$::env(WIN) {} { foreach d {2 6 10 14 18 22 26 30 40} { after time $d [list dump w+$d] } }
skip
after time $::env(END) { puts $::fh " end"; close $::fh; exit }
