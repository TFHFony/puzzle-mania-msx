source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle on
dstep {[peek 0xC00F] == 50} { }
dstep {[peek 0xC1EF] >= 1 && [peek 0xC1EF] != 255} { record start -audioonly "F:/MSX Projects/PMdev26/work/shots/rec.wav" }
dpause 3
dstep 1 { shot 123_title }
dpause 1.5
dstep 1 { record stop; exit }
drun
after time 60 { exit }
