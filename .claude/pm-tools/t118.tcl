source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
dstep {[peek 0xC00F] == 50} { }
dpause 9
dstep 1 { log "sccm=[peek 0xC37A] mus_on=[peek 0xC0D0] trk=[peek 0xC0D1] bank=[expr {[peek 0xC0D2]+256*[peek 0xC0D3]}] s=[expr {[peek 0xC0D6]+256*[peek 0xC0D7]}] e=[expr {[peek 0xC0D8]+256*[peek 0xC0D9]}] f=[peek 0xC0DB]"; exit }
drun
after time 40 { exit }
