# puzzle moves drawn by the job engine, then a full redraw (N held and released): the two screens must be identical
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle on
debug set_bp 0x4020 {} {
  for {set a 0xC000} {$a < 0xEFFF} {incr a} { poke $a [expr {int(rand()*256)}] }
  reg BC2 0xFF98; reg DE2 0x5A5A; reg HL2 0x1234; reg AF2 0xFF44
}
dstep {[peek 0xC00F] == 50} { }
dpause 6
dstep 1 { key 8 0x01 0.2 }
dpause 4
dstep 1 { key 8 0x01 0.2 }
dpause 3
dstep 1 { key 8 0x01 0.2 }
dpause 3
dstep 1 { key 8 0x10 0.15 }
dpause 0.7
dstep 1 { key 8 0x20 0.15 }
dpause 0.7
dstep 1 { key 8 0x80 0.15 }
dpause 0.7
dstep 1 { key 8 0x40 0.15 }
dpause 0.7
dstep 1 { key 8 0x10 0.15 }
dpause 0.7
dstep 1 { key 8 0x20 0.15 }
dpause 0.7
dstep 1 { key 8 0x80 0.15 }
dpause 2
dstep 1 { log "moves=[peek 0xC0F0] qn=[peek 0xC15B]"; shot 64a }
dpause 0.5
dstep 1 { key 4 0x08 0.6 }
dpause 2
dstep 1 { shot 64b; exit }
drun
