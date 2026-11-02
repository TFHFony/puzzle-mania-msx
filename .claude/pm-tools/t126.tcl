source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle on
dstep {[peek 0xC00F] == 50} { }
dstep {[peek 0xC1EF] >= 20 && [peek 0xC1EF] < 255} { shot 126_title; log "sccm=[peek 0xC37A] msx=[peek 0xC1FC]" }
dstep {[peek 0xC1FD] == 1} { }
dpause 3
dstep 1 { shot 126_menu; exit }
drun
after time 60 { exit }
