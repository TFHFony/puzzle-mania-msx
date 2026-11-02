source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle on
dstep {[peek 0xC00F] == 50} { }
dstep {[peek 0xC1EF] >= 60 && [peek 0xC1EF] < 150} { shot 112_title; exit }
drun
