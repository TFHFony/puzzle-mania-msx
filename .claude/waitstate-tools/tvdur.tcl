# the length of the title video with the loop FORCE (0 = 446, 1 = 438): breakpoints at the entries / exits of the player.  ENT, EX = hex addresses
set throttle off
set ::t0 -1
after time 7 { poke 0xC391 $::env(FORCE) }
foreach a $::env(ENT) { debug set_bp $a {} { if {$::t0 < 0} { set ::t0 [machine_info time] } } }
foreach a $::env(EX) { debug set_bp $a {} { set f [open $::env(OUT) w]; puts $f [format "start %.3f end %.3f dur %.3f tvd=%d" $::t0 [machine_info time] [expr {[machine_info time] - $::t0}] [peek 0xC391]]; close $f; exit } }
after time 150 { exit }
