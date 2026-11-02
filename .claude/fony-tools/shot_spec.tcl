# holds S from the start (the specs screen), screenshots at 4, 7, 12 s: SHOT=<prefix>
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle on
after time 600 { exit }
keymatrixdown 5 1
foreach t {4 7 12} { dstep "\[machine_info time\] >= $t" "screenshot \"$::env(SHOT)_$t.png\"" }
dstep {[machine_info time] >= 13} { exit }
drun
