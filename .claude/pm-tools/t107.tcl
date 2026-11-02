source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle on
dstep {[peek 0xC00F] == 50} { }
dpause 8
dstep 1 { key 8 0x01 0.2 }
dpause 4
dstep 1 { shot 107_menu; exit }
drun
