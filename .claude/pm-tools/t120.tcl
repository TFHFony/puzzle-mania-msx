source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle on
dstep {[peek 0xC00F] == 50} { }
dpause 8
dstep {[peek 0xC0D0] == 1 && [peek 0xC0D1] == 0} { record start -audioonly "F:/MSX Projects/PMdev26/work/shots/rec.wav" }
dpause 8
dstep 1 { record stop; log "recorded mus_on=[peek 0xC0D0] sccm=[peek 0xC37A]"; exit }
drun
after time 60 { exit }
