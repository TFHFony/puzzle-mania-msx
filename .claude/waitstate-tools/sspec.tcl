# S held from the start: the specs screen; shot at T1, C pressed, shot, SELECT pressed, shot.  SHOT=<prefix>
set throttle on
set frameskip 0
set T $::env(T1)
keymatrixdown 5 1
after time $T "screenshot \"$::env(SHOT)_a.png\"; keymatrixdown 3 1"
after time [expr {$T + 0.4}] "keymatrixup 3 1"
after time [expr {$T + 1.5}] "screenshot \"$::env(SHOT)_b.png\"; keymatrixdown 7 0x40"
after time [expr {$T + 1.9}] "keymatrixup 7 0x40"
after time [expr {$T + 3}] "screenshot \"$::env(SHOT)_c.png\"; set f \[open \"$::env(SHOT).txt\" w\]; puts \$f \"wait=\[peek 0xC390\] tvd=\[peek 0xC391\] hz=\[peek 0xC00F\]\"; close \$f"
after time [expr {$T + 3.5}] { exit }
