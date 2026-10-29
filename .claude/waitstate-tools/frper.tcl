# the period of the frames of the menu (calls of mvsync_) while the menu is idle: hits 1..300 after ::env(T0)
set throttle off
set ::ts {}
set ::go 0
after time $::env(T0) { set ::go 1 }
if {[info exists ::env(KEYROW)]} { after time [expr {$::env(T0) - 1}] { keymatrixdown $::env(KEYROW) $::env(KEYMASK) } }
debug set_bp $::env(ADDR) {} { if {$::go && [llength $::ts] < 300} { lappend ::ts [machine_info time] } ; if {[llength $::ts] >= 300} { set f [open $::env(OUT) w]; puts $f $::ts; close $f; exit } }
after time 100 { exit }
