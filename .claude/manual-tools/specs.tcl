set throttle off
keymatrixdown 5 1
proc shot {n} { set ::throttle on; after time 0.6 [list shot2 $n] }
proc shot2 {n} { screenshot "$::env(OUT).png"; exit }
after time 12 { shot 1 }
after time 40 { exit }
