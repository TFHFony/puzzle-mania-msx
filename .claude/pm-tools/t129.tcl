source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
dstep {[peek 0xC00F] == 50 || [peek 0xC00F] == 60} { }
dstep {[peek 0xC0D0] == 1 && [peek 0xC0D1] == 0} { }
dpause 1
dstep 1 { log "before: hz=[peek 0xC00F] r9=[format %02X [peek 0xFFE8]] mus_f=[peek 0xC0DB] trk=[peek 0xC0D1] on=[peek 0xC0D0]"; key 7 0x40 0.3 }
dpause 1
dstep 1 { log "after SELECT: hz=[peek 0xC00F] r9=[format %02X [peek 0xFFE8]] mus_f=[peek 0xC0DB] trk=[peek 0xC0D1] on=[peek 0xC0D0]"; key 7 0x40 0.3 }
dpause 1
dstep 1 { log "after SELECT 2: hz=[peek 0xC00F] r9=[format %02X [peek 0xFFE8]] mus_f=[peek 0xC0DB]"; exit }
drun
after time 80 { exit }
