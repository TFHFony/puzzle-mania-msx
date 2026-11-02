# S held at the start: the specs screen; ESC goes on
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle on
keymatrixdown 5 0x01
dstep {[peek 0xC00F] == 50 || [peek 0xC00F] == 60} { }
dpause 3
dstep 1 { shot 127_spec; log "hz=[peek 0xC00F] r9=[format %02X [peek 0xFFE8]] msx=[peek 0x002D]"; keymatrixup 5 0x01; key 7 0x04 0.3 }
dpause 4
dstep 1 { shot 127_after; log "tv_f=[peek 0xC1EF] on=[peek 0xC0D0]"; exit }
drun
after time 50 { exit }
