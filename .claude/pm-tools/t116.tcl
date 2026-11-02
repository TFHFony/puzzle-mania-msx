source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
set ::o {}
set ::on 0
debug set_bp 0x4499 {} { if {$::on && [llength $::o] < 30} { lappend ::o "after in A9: a=[format %02X [reg A]] b=[format %02X [reg B]] sp=[format %04X [reg SP]] byte4495=[format %02X [peek 0x4495]] pc=[format %04X [reg PC]]" } }
dstep {[peek 0xC00F] == 50} { }
dpause 12
dstep 1 { set ::on 1 }
dpause 0.1
dstep 1 { set fh [open "F:/MSX Projects/PMdev26/work/shots/t116.txt" w]; puts $fh [join $::o "\n"]; close $fh; exit }
drun
