# check of the 10 photo ROM: title video, menu, photo 10 (STEF), its size menu and puzzle, the reward clip.   DUMP=<prefix> openmsx -machine M -cart PuzzleMania_128MB.rom -romtype NEO-16 -script stef_check.tcl
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle on
after time 170 { exit }
dstep {[peek 0xC00F] == 50 || [peek 0xC00F] == 60} { log start }
dpause 7
dstep 1 { shot 01_title_a }
dpause 9
dstep 1 { shot 02_title_b }
dpause 8
dstep 1 { shot 03_title_c; key 8 0x01 0.2 }
dpause 5
dstep 1 { shot 04_menu }
dstep 1 { key 8 0x80 0.2 }
dpause 0.8
dstep 1 { key 8 0x80 0.2 }
dpause 0.8
dstep 1 { key 8 0x80 0.2 }
dpause 0.8
dstep 1 { key 8 0x80 0.2 }
dpause 0.8
dstep 1 { key 8 0x40 0.2 }
dpause 1.5
dstep 1 { shot 05_menu_last; key 8 0x01 0.2 }
dpause 3
dstep 1 { shot 06_size; key 8 0x80 0.2 }
dpause 0.5
dstep 1 { key 8 0x01 0.2 }
dstep {[peek 0xC0D1] == 1 && [peek 0xC0DF] == 0 && [peek 0xC024] == 16} { log "puzzle" }
dpause 2.5
dstep 1 { shot 07_puzzle }
dstep 1 { for {set i 0} {$i<16} {incr i} {poke [expr 0xC100+$i] $i}; poke 0xC10E 15; poke 0xC10F 14; poke 0xC025 2; poke 0xC026 3; poke 0xC0F0 87; poke 0xC0F2 154 }
dpause 0.3
dstep 1 { key 8 0x10 0.2 }
dpause 1.6
dstep 1 { shot 08_solved }
dpause 6
dstep 1 { shot 09_video_a }
dpause 15
dstep 1 { shot 10_video_b; exit }
drun
