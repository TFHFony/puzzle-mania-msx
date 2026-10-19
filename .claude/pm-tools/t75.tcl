# N, H, L in the puzzle: after each of them the screen must be the same as before (the puzzle did not change)
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle on
dstep {[peek 0xC00F] == 50} { }
dpause 6
dstep 1 { key 8 0x01 0.2 }
dpause 4
dstep 1 { key 8 0x01 0.2 }
dpause 3
dstep 1 { key 8 0x01 0.2 }
dpause 4
dstep 1 { key 8 0x20 0.15 }
dpause 1.5
dstep 1 { key 8 0x10 0.15 }
dpause 1.5
dstep 1 { key 8 0x40 0.15 }
dpause 2
dstep 1 { log "lines=[peek 0xC019] moves=[peek 0xC0F0]"; shot 75a; key 4 0x08 0.6 }
dpause 0.2
dstep 1 { shot 75n }
dpause 1.5
dstep 1 { shot 75b; key 3 0x20 0.6 }
dpause 3
dstep 1 { shot 75c }
dpause 0.1
dstep 1 { key 4 0x02 0.15 }
dpause 3
dstep 1 { key 4 0x02 0.15 }
dpause 3
dstep 1 { key 4 0x02 0.15 }
dpause 3
dstep 1 { log "lines=[peek 0xC019]"; shot 75d; exit }
drun
