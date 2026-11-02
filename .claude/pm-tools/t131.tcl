# menu logo: screenshots of the menu, after scrolling and (S held) the specs screen
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
dpause 6
dstep 1 { key 8 0x01 0.2 }
dpause 3
dstep 1 { key 8 0x01 0.2 }
dpause 10
dstep 1 { shot menu }
dstep 1 { key 8 0x80 0.2 }
dpause 3
dstep 1 { shot scrolled }
dstep 1 { key 8 0x80 0.2 }
dpause 3
dstep 1 { shot scrolled2; exit }
drun
