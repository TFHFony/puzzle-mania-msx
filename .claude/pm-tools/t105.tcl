# screenshots of the MSX2 version: title (photo or video), menu, puzzle, solved
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle on
dstep {[peek 0xC00F] == 50} { }
dstep {[peek 0xC1FD] == 11 || [peek 0xC1FD] == 0 && [peek 0xC0D0] == 1} { }
dpause 3
dstep 1 { shot 105_title }
dstep {[peek 0xC1FD] == 1} { }
dpause 4
dstep 1 { shot 105_menu }
dstep {[peek 0xC1F7] == 1 && [peek 0xC0F0] >= 8 && [peek 0xC0D0] == 1} { shot 105_puzzle }
dstep {[peek 0xC1F7] == 1 && [peek 0xC0D0] == 0 && [peek 0xC0F0] >= 30} { }
dpause 1.5
dstep 1 { shot 105_win }
dstep {[peek 0xC1F7] == 0} { exit }
drun
