set throttle off
proc shot {n} { set ::throttle on; after time 0.6 [list shot2 $n] }
proc shot2 {n} { screenshot "$::env(OUT)_$n.png"; set ::throttle off }
for {set t 8} {$t <= 70} {incr t 2} { after time $t [list shot [format %03d $t]] }
after time 74 { exit }
