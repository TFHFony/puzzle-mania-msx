set throttle off
set frameskip 0
after time $::env(T0) { record start $::env(WAV) }
after time [expr {$::env(T0) + 12}] { record stop; exit }
after time 120 { exit }
