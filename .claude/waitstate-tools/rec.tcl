set throttle off
set frameskip 0
after time 40 { record start $::env(WAV) }
after time 52 { record stop; exit }
after time 100 { exit }
