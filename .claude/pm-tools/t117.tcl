source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
set ::o {}
proc w {} { lappend ::o "t=[format %.2f [machine_info time]] k8=[format %02X [peek 0xC0E0]] k7=[format %02X [peek 0xC0E1]] joy=[format %02X [peek 0xC1EE]] jc=[format %02X [peek 0xC37D]] frame=[peek 0xC009]"; after time 0.2 w }
dstep {[peek 0xC00F] == 50} { }
dpause 7
dstep 1 { w; keymatrixdown 8 0x01 }
dpause 1.5
dstep 1 { keymatrixup 8 0x01 }
dpause 1
dstep 1 { set fh [open "F:/MSX Projects/PMdev26/work/shots/t117.txt" w]; puts $fh [join $::o "\n"]; close $fh; exit }
drun
