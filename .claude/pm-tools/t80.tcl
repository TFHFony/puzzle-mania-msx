# screenshots of the screens built by the job engine
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle on
dstep {[peek 0xC00F] == 50} { }
dpause 6
dstep 1 { key 8 0x01 0.2 }
dpause 4
dstep 1 { shot 80_menu; key 8 0x80 0.15 }
dpause 0.2
dstep 1 { key 8 0x80 0.15 }
dpause 3
dstep 1 { shot 80_scrolled; key 3 0x20 0.3 }
dpause 4
dstep 1 { shot 80_help1; key 8 0x01 0.2 }
dpause 4
dstep 1 { shot 80_help2; key 8 0x01 0.2 }
dpause 4
dstep 1 { shot 80_menu_back; key 7 0x04 0.2 }
dpause 4
dstep 1 { shot 80_credits; key 8 0x01 0.2 }
dpause 4
dstep 1 { key 8 0x01 0.2 }
dpause 4
dstep 1 { shot 80_size; key 8 0x01 0.2 }
dpause 8
dstep 1 { shot 80_puzzle; key 3 0x20 0.6 }
dpause 1.5
dstep 1 { shot 80_H }
dpause 2
dstep 1 { shot 80_Hback; exit }
drun
