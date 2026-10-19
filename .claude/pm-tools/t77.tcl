source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
dstep {[peek 0xC00F] == 50} { log start }
dpause 4
dstep 1 { key 8 0x01 0.2 }
dpause 4
dstep 1 { key 8 0x01 0.2 }
dpause 3
dstep 1 { key 7 0x04 0.2 }
dpause 3
dstep 1 { key 8 0x01 0.2 }
dpause 3
dstep 1 { key 8 0x01 0.2 }
dpause 8
dstep 1 { for {set i 0} {$i<9} {incr i} {poke [expr 0xC100+$i] $i}; poke 0xC107 8; poke 0xC108 7; poke 0xC025 1; poke 0xC026 2; key 8 0x10 0.2 }
dstep {[peek 0xC0D1] == 2} { log jingle; record start "F:/MSX Projects/PMdev26/work/shots/jingle_rec.wav" -audioonly }
dpause 4.3
dstep 1 { record stop; log done; set throttle on }
dpause 3
dstep 1 { set h 0; for {set i 0} {$i < 400} {incr i 7} { set h [expr {($h*31 + [vpeek $i]) & 0xFFFFFF}] }; log "vram hash=$h"; shot 77_video; log "mus_on=[peek 0xC0D0] pc=[format %04X [reg PC]] sp=[format %04X [reg SP]] vleft=[peek 0xC042]+[peek 0xC043]"; key 8 0x01 0.2 }
dpause 0.7
dstep 1 { set h 0; for {set i 0} {$i < 400} {incr i 7} { set h [expr {($h*31 + [vpeek $i]) & 0xFFFFFF}] }; log "vram hash later=$h" }
dpause 2
dstep 1 { shot 77_after; log "after SPACE hz=[peek 0xC00F]"; exit }
drun
