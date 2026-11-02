# the size menu of the MSX2 version
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle on
dstep {[peek 0xC00F] == 50} { }
dstep {[peek 0xC1FD] == 1} { }
dpause 2
dstep 1 { key 8 0x40 0.15 }
dpause 1
dstep 1 { key 8 0x01 0.2 }
dpause 4
dstep 1 { shot 111_size; log "v_pal=[peek 0xC1FD] photo=[peek 0xC000]"; exit }
drun
