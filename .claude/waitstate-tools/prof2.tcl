# profile of busy puzzle frames: time at every instruction of the code bank + the player markers, 14 frames from the first busy frame after the first key press in the puzzle
set throttle off
set ::cap 0
set ::nf 0
set ::L {}
proc key {row mask t0 dur} { after time $t0 "keymatrixdown $row $mask"; after time [expr {$t0 + $dur}] "keymatrixup $row $mask" }
key 8 1 47 0.3
key 8 1 52 0.3
set t 60
foreach k {0x10 0x20 0x80 0x40 0x10 0x20 0x80 0x40} { key 8 $k $t 0.12; set t [expr {$t + 0.7}] }
set ::armed 0
after time 59.5 { set ::armed 1 }
debug set_bp 0xD300 {} {
  if {$::armed && !$::cap && [peek 0xC148] != 0} { set ::cap 1; set ::nf 0 }
  if {$::cap} { incr ::nf; lappend ::L "M 0 [format %.9f [machine_info time]]"
    if {$::nf > 14} { set f [open $::env(OUT) w]; puts $f [join $::L "\n"]; close $f; exit } }
}
debug set_bp 0xE2CB {} { if {$::cap} { lappend ::L "P 0 [format %.9f [machine_info time]]" } }
foreach a $::env(ADDRS) { debug set_bp $a {} { if {$::cap} { lappend ::L "I [format %04X [reg PC]] [format %.9f [machine_info time]]" } } }
after time 200 { exit }
