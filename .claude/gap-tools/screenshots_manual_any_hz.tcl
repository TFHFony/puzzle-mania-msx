# screenshots for the manual: the 128 MB ROM on an MSX2 (PAL), the photo of FH.mp4 (photo 2: from the first photo the cursor goes one column to the right), a 4x4 puzzle, the reward video of FH.mp4.
# TIT=1: the title photo comes first (02_title), TIT=0: the title video (02b / 02c).
#   TIT=1 DUMP=F:/.../work/manual/a openmsx -machine Philips_NMS_8250 -cart PuzzleMania_128MB.rom -romtype NEO-16 -script screenshots_manual.tcl
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle on
after time 600 { exit }
dstep {[peek 0xC00F] == 50 || [peek 0xC00F] == 60} { poke 0xC1F9 $::env(TIT); log "start tit=$::env(TIT)" }
dpause 2.4
dstep 1 { shot 01_fony }
if {$::env(TIT) == 0} {
  dstep {[peek 0xC1F9] == 1} { log "title video" }
  dpause 9
  dstep 1 { shot 02b_title_video }
  dpause 9
  dstep 1 { shot 02c_title_video; exit }
} else {
  dstep {[peek 0xC0D0] == 1 && [peek 0xC0D1] == 0} { log "title photo" }
  dpause 3
  dstep 1 { shot 02_title; key 8 0x01 0.2 }
  dpause 4.5
  dstep 1 { key 8 0x80 0.2 }
  dpause 1.5
  dstep 1 { log "FH selected? v_sel=[peek 0xC002] (must be 2)"; shot 06_menu; key 3 0x20 0.2 }
  dpause 3
  dstep 1 { shot 03_howto1; key 8 0x01 0.2 }
  dpause 3
  dstep 1 { shot 04_howto2; key 8 0x01 0.2 }
  dpause 3
  dstep 1 { key 7 0x04 0.2 }
  dpause 3
  dstep 1 { shot 16_credits; key 8 0x01 0.2 }
  dpause 4
  dstep 1 { log "before choosing: v_sel=[peek 0xC002]"; key 8 0x01 0.2 }
  dpause 4
  dstep 1 { log "photo=[peek 0xC000] (must be 2)"; shot 08_size; key 8 0x80 0.2 }
  dpause 0.5
  dstep 1 { key 8 0x01 0.2 }
  dstep {[peek 0xC0D1] == 1 && [peek 0xC0DF] == 0 && [peek 0xC024] == 16} { log "puzzle photo=[peek 0xC000]" }
  dpause 2.5
  dstep 1 { shot 09_puzzle4; keymatrixdown 4 0x08 }
  dpause 1.5
  dstep 1 { shot 10_numbers; keymatrixup 4 0x08 }
  dpause 1.5
  dstep 1 { key 5 0x02 0.2 }
  dpause 0.15
  dstep 1 { shot 11_hint }
  dpause 0.25
  dstep 1 { shot 11b_hint }
  dpause 0.25
  dstep 1 { shot 11c_hint }
  dpause 2.5
  dstep 1 { key 4 0x02 0.2 }
  dpause 2
  dstep 1 { shot 13a_lines }
  dpause 0.3
  dstep 1 { key 4 0x02 0.2 }
  dpause 2
  dstep 1 { shot 13b_lines }
  dpause 0.3
  dstep 1 { key 4 0x02 0.2 }
  dpause 2
  dstep 1 { shot 13c_lines }
  dpause 0.3
  dstep 1 { keymatrixdown 3 0x20 }
  dpause 2
  dstep 1 { shot 13_solution; keymatrixup 3 0x20 }
  dpause 2
  dstep 1 { for {set i 0} {$i<16} {incr i} {poke [expr 0xC100+$i] $i}; poke 0xC10E 15; poke 0xC10F 14; poke 0xC025 2; poke 0xC026 3; poke 0xC0F0 87; poke 0xC0F2 154 }
  dpause 0.3
  dstep 1 { key 8 0x10 0.2 }
  dpause 1.6
  dstep 1 { shot 14_solved }
  dpause 14
  dstep 1 { shot 15_video; key 8 0x01 0.3 }
  dpause 5
  dstep 1 { key 8 0x01 0.2 }
  dpause 4
  dstep 1 { key 3 0x01 0.2 }
  dpause 1.5
  dstep 1 { shot 08b_size_cursor; key 8 0x01 0.2 }
  dstep {[peek 0xC0D1] == 1 && [peek 0xC0DF] == 0 && [peek 0xC024] == 9} { log "puzzle 3x3" }
  dpause 3
  dstep 1 { key 8 0x80 0.2 }
  dpause 0.8
  dstep 1 { key 8 0x40 0.2 }
  dpause 1.5
  dstep 1 { shot 12_cursor_mode; key 7 0x04 0.2 }
  dpause 4
  dstep 1 { key 8 0x80 0.2 }
  dpause 1
  dstep 1 { key 8 0x80 0.2 }
  dpause 1.5
  dstep 1 { shot 07_menu_scrolled; exit }
}
drun
