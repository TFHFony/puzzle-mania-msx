source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle on
dstep {[peek 0xC00F] == 50} { }
dpause 7
dstep 1 { shot 114_title; key 8 0x01 0.2 }
dpause 4
dstep 1 { shot 114_menu; log "sccm=[peek 0xC37A] on=[peek 0xC0D0] busy=[peek 0xC148] jqn=[peek 0xC1E2]"; exit }
drun
