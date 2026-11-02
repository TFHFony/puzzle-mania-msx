# the photo menu with a held cursor key: sample v_sel / v_win while RIGHT is held, then DOWN held, then in the size menu LEFT/DOWN held
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
set ::R {}
proc smp {tag} { lappend ::R "$tag t=[format %.2f [machine_info time]] sel=[peek 0xC002] win=[peek 0xC066] ssel=[peek 0xC06B] busy=[peek 0xC148]" }
dstep {[peek 0xC00F] == 50} { }
dpause 5.5
dstep 1 { key 8 0x01 0.2 }
dpause 6
dstep 1 { smp start; keymatrixdown 8 0x80 }
for {set i 0} {$i < 8} {incr i} { dpause 0.4; dstep 1 { smp hold_right } }
dstep 1 { keymatrixup 8 0x80 }
dpause 1
dstep 1 { smp after_right; keymatrixdown 8 0x10 }
for {set i 0} {$i < 8} {incr i} { dpause 0.4; dstep 1 { smp hold_left } }
dstep 1 { keymatrixup 8 0x10 }
dpause 1
dstep 1 { smp after_left; key 8 0x01 0.2 }
dpause 3
dstep 1 { smp size_menu; keymatrixdown 8 0x80 }
dpause 0.6
dstep 1 { smp size_right; keymatrixup 8 0x80; keymatrixdown 8 0x40 }
dpause 0.6
dstep 1 { smp size_down; keymatrixup 8 0x40; set f [open $::env(OUT) w]; puts $f [join $::R "\n"]; close $f; exit }
drun
