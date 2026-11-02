# the SCC16 player: time and PC of every frequency write (9880h: one per sample) and of the VDP writes, in the menu (music + drawing)
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
set ::L {}
set ::on 0
debug set_watchpoint write_mem 0x9880 {} { if {$::on} { lappend ::L "s [format %.7f [machine_info time]] [format %04X [reg PC]]" } }
debug set_watchpoint write_io {0x98 0x99} {} { if {$::on} { lappend ::L "v [format %.7f [machine_info time]] $::wp_last_address" } }
dstep {[peek 0xC00F] == 50} { }
dpause 6
dstep 1 { set ::on 1; key 8 0x01 0.2 }
dpause 3
dstep 1 { set ::on 0; set fh [open "F:/MSX Projects/PMdev26/work/shots/t113.txt" w]; puts $fh [join $::L "\n"]; close $fh; exit }
drun
