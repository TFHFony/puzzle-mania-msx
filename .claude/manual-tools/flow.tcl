# screenshots for the manual: a list of steps run after the choice screen is reached. env: ML (mode_loop), OUT (prefix), FLOW (a|b)
set throttle off
set ::choice 0
proc key {row mask} { keymatrixdown $row $mask; after time 0.12 [list keymatrixup $row $mask] }
proc skip {} { if {!$::choice} { key 8 1; after time 0.7 skip } }
proc shot {n} { set ::throttle on; after time 0.6 [list shot2 $n] }
proc shot2 {n} { screenshot "$::env(OUT)_$n.png"; set ::throttle off; next }
proc wait {s} { after time $s next }
proc run {steps} { set ::steps $steps; next }
proc next {} {
    if {[llength $::steps] == 0} { exit }
    set s [lindex $::steps 0]; set ::steps [lrange $::steps 1 end]
    switch [lindex $s 0] {
        key { key [lindex $s 1] [lindex $s 2]; after time 0.3 next }
        wait { wait [lindex $s 1] }
        shot { shot [lindex $s 1] }
    }
}
set A {
 {wait 2} {shot choice}
 {key 7 4} {wait 2.5} {shot credits} {key 8 1} {wait 4}
 {key 8 1} {wait 4} {shot photomenu}
 {key 3 32} {wait 1.5} {shot help1} {key 8 1} {wait 1.5} {shot help2} {key 7 4} {wait 2}
 {key 8 1} {wait 3} {shot sizemenu}
 {key 8 1} {wait 7} {shot puzzle}
 {key 3 32} {wait 1} {shot solution}
}
set C {
 {wait 2} {key 8 1} {wait 4} {key 8 1} {wait 3} {key 3 1} {wait 1} {shot csize}
 {key 8 1} {wait 7} {shot c0}
 {key 8 128} {wait 0.7} {shot c1}
 {key 8 1} {wait 1.0} {shot c2}
 {key 8 32} {wait 0.7} {shot c3}
 {key 8 1} {wait 1.0} {shot c4}
}
set B {
 {wait 2} {key 8 128} {wait 0.5} {shot choice_memory}
 {key 8 1} {wait 6} {shot board}
 {key 8 1} {wait 1} {key 8 128} {wait 0.5} {key 8 1} {wait 0.4} {shot flipped}
 {wait 2} {key 8 1} {wait 1} {key 8 128} {wait 0.2} {key 8 128} {wait 0.5} {key 8 1} {wait 0.4} {shot flipped2}
}
debug set_bp 0x$::env(ML) {} { if {!$::choice} { set ::choice 1; run [set ::$::env(FLOW)] } }
skip
after time 300 { exit }
