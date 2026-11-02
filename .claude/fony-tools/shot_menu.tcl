# boot, screenshots at 48 s and 56 s of emulated time (SHOT=<prefix>)
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
after time 600 { exit }
dstep {[machine_info time] >= 48} { screenshot "$::env(SHOT)_48.png" }
dstep {[machine_info time] >= 56} { screenshot "$::env(SHOT)_56.png"; exit }
drun
