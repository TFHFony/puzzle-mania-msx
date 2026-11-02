# help pages and credits after the exact text coding
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
dpause 6
dstep 1 { key 8 0x01 0.2 }
dpause 3
dstep 1 { key 8 0x01 0.2 }
dpause 14
dstep 1 { key 3 0x20 0.3 }
dpause 6
dstep 1 { shot help1; key 8 0x01 0.2 }
dpause 4
dstep 1 { shot help2; key 7 0x04 0.2 }
dpause 2
dstep 1 { key 7 0x04 0.2 }
dpause 2
dstep 1 { key 7 0x04 0.2 }
dpause 3
dstep 1 { shot third; exit }
drun
