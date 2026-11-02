# attract on photo PHOTO (3x3), screenshots of the clip after the win: SHOT=<prefix> -> <prefix>_a.png, _b.png, _c.png
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
after time 1500 { exit }
dstep {[peek 0xC00F] == 50 || [peek 0xC00F] == 60} { for {set i 0} {$i < 10} {incr i} {poke [expr 0xC300 + $i] [expr {$i != $::env(PHOTO)}]} }
dstep {[peek 0xC1F7] == 1} { poke 0xC380 3; log "attract on" }
dstep {[peek 0xC0D1] == 3 && [peek 0xC0D0] == 1} { log "win jingle started" }
dpause 8
dstep 1 { screenshot "$::env(SHOT)_00.png" }
dpause 3
dstep 1 { screenshot "$::env(SHOT)_01.png" }
dpause 3
dstep 1 { screenshot "$::env(SHOT)_02.png" }
dpause 3
dstep 1 { screenshot "$::env(SHOT)_03.png" }
dpause 3
dstep 1 { screenshot "$::env(SHOT)_04.png" }
dpause 3
dstep 1 { screenshot "$::env(SHOT)_05.png" }
dpause 3
dstep 1 { screenshot "$::env(SHOT)_06.png" }
dpause 3
dstep 1 { screenshot "$::env(SHOT)_07.png" }
dpause 3
dstep 1 { screenshot "$::env(SHOT)_08.png" }
dpause 3
dstep 1 { screenshot "$::env(SHOT)_09.png" }
dpause 3
dstep 1 { screenshot "$::env(SHOT)_10.png" }
dpause 3
dstep 1 { screenshot "$::env(SHOT)_11.png" }
dpause 3
dstep 1 { screenshot "$::env(SHOT)_12.png" }
dpause 3
dstep 1 { exit }
drun
