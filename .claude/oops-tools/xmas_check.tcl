# photo 12 (Xmas2026), last column holds two photos: menu carousel to the last column, size menu, puzzle, reward video.  TIT=1 DUMP=F:/.../work/oops/a
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle on
after time 700 { exit }
dstep {[peek 0xC00F] == 50} { poke 0xC1F9 1; log "start" }
dstep {[peek 0xC0D0] == 1 && [peek 0xC0D1] == 0} { log "title photo" }
dpause 3
dstep 1 { key 8 0x01 0.2 }
dpause 4.5
dstep 1 { shot 01_menu; log "menu win=[peek 0xC066] sel=[peek 0xC002]" }
for {set i 0} {$i < 5} {incr i} {
  dstep 1 { key 8 0x80 0.2 }
  dpause 1.2
  dstep 1 { log "right: win=[peek 0xC066] sel=[peek 0xC002]" }
}
dstep 1 { shot 02a_last_column; key 8 0x40 0.2 }
dpause 1
dstep 1 { shot 02_last_column; log "down: win=[peek 0xC066] sel=[peek 0xC002] (must be 11)"; key 8 0x10 0.2 }
dpause 1.2
dstep 1 { log "left: win=[peek 0xC066] sel=[peek 0xC002] (9)"; shot 03_after_left; key 8 0x80 0.2 }
dpause 1.2
dstep 1 { log "right again: win=[peek 0xC066] sel=[peek 0xC002] (11)"; key 8 0x01 0.2 }
dpause 4
dstep 1 { log "size menu: photo=[peek 0xC000] pal=[peek 0xC1FD]"; shot 04_size; key 8 0x80 0.2 }
dpause 0.5
dstep 1 { key 8 0x01 0.2 }
dstep {[peek 0xC0D1] == 1 && [peek 0xC0DF] == 0 && [peek 0xC024] == 16} { log "puzzle photo=[peek 0xC000] pal=[peek 0xC1FD]" }
dpause 2.5
dstep 1 { shot 05_puzzle4; keymatrixdown 3 0x20 }
dpause 2
dstep 1 { shot 06_solution; keymatrixup 3 0x20 }
dpause 1
dstep 1 { for {set i 0} {$i<16} {incr i} {poke [expr 0xC100+$i] $i}; poke 0xC10E 15; poke 0xC10F 14; poke 0xC025 2; poke 0xC026 3; poke 0xC0F0 87; poke 0xC0F2 154 }
dpause 0.3
dstep 1 { key 8 0x10 0.2 }
dpause 1.6
dstep 1 { shot 07_solved }
dpause 14
dstep 1 { shot 08_video; log "video start"; }
dpause 20
dstep 1 { shot 09_video2 }
dpause 25
dstep 1 { shot 10_video3; exit }
drun
