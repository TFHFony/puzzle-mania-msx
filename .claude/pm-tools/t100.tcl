# the SCC jingle: writes to the SCC registers (9880h..988Fh) during the win screen
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
set ::L {}
debug set_watchpoint write_mem {0x9880 0x988F} {} { if {[peek 0xC1F7] == 1} { lappend ::L "[format %.3f [machine_info time]] [format %04X $::wp_last_address] $::wp_last_value" } }
dstep {[peek 0xC00F] == 50} { }
dpause 6
dstep 1 { key 8 0x01 0.2 }
dstep {[peek 0xC1F7] == 1 && [llength $::L] > 20} { log "scc=[peek 0xC1FE] slot=[format %02X [peek 0xC1FF]] own=[format %02X [peek 0xC1F6]]" }
dstep {[peek 0xC1F7] == 0 && [llength $::L] > 20} { log "back in the menu; writes [llength $::L]"; set fh [open "F:/MSX Projects/PMdev26/work/shots/t100.txt" w]; puts $fh [join $::L "\n"]; close $fh; exit }
drun
