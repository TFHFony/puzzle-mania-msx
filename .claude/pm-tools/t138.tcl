# S screen: P switches the palette to the MSX1 colours; the menu afterwards
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle on
keymatrixdown 5 0x01
dstep {[peek 0xC00F] == 50 || [peek 0xC00F] == 60} { }
dpause 4
dstep 1 { shot spec1; key 4 0x20 0.3 }
dpause 3
dstep 1 { shot spec2; log "v_msx=[peek 0xC1FC] v_pb=[expr {[peek 0xC1FA]+256*[peek 0xC1FB]}]"; keymatrixup 5 0x01; key 7 0x04 0.3 }
drun
