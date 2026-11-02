source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
keymatrixdown 5 0x01
dstep {[peek 0xC00F] == 50 || [peek 0xC00F] == 60} { }
dpause 3
dstep 1 { shot spec; exit }
drun
