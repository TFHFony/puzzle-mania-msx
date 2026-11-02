# new documentation screenshots: menu, scrolled menu, help 1/2, 2/2, credits
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
dpause 6
dstep 1 { key 8 0x01 0.2 }
dpause 3
dstep 1 { key 8 0x01 0.2 }
dpause 14
dstep 1 { shot menu }
dstep 1 { key 8 0x80 0.2 }
dpause 1.5
dstep 1 { key 8 0x80 0.2 }
dpause 1.5
dstep 1 { key 8 0x80 0.2 }
dpause 12
dstep 1 { shot scrolled }
dstep 1 { key 3 0x20 0.3 }
dpause 14
dstep 1 { shot help1; key 8 0x01 0.2 }
dpause 14
dstep 1 { shot help2; key 8 0x01 0.2 }
dpause 14
dstep 1 { key 7 0x04 0.2 }
dpause 14
dstep 1 { shot credits; exit }
drun
