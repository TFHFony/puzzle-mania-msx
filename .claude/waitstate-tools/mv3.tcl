# real play: select photo 0, size, then arrow keys; per frame (mvsync_ calls): time, mus_sk, mus_n, mus_pl, j_qn
set throttle off
set ::L {}
set ::on 0
proc key {row mask t0 dur} { after time $t0 "keymatrixdown $row $mask"; after time [expr {$t0 + $dur}] "keymatrixup $row $mask" }
key 8 1 47 0.3
key 8 1 52 0.3
set t 60
foreach k {0x10 0x20 0x80 0x40 0x10 0x20 0x80 0x40 0x10 0x20 0x80 0x40 0x10 0x20 0x80 0x40} { key 8 $k $t 0.12; set t [expr {$t + 0.6}] }
after time 58 { set ::on 1 }
debug set_bp 0xD300 {} { if {$::on} { lappend ::L "M [format %.7f [machine_info time]] [peek 0xC142] [peek 0xC1ED]"; if {[machine_info time] > 70} { set f [open $::env(OUT) w]; puts $f [join $::L "
"]; close $f; exit } } }
debug set_bp 0xE2CB {} { if {$::on} { lappend ::L "P [format %.7f [machine_info time]] 0 0" } }
after time 200 { exit }
