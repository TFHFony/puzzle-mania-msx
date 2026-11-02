source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
dpause 6
dstep 1 { key 8 0x01 0.2 }
dpause 3
dstep 1 { key 8 0x01 0.2 }
dpause 14
dstep 1 { key 7 0x04 0.4 }
dpause 12
dstep 1 { shot credits; exit }
drun
