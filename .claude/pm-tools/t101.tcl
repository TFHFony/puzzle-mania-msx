# the SCC player: time of the sample writes (9800h) in the menu music; v_sccm / pages
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
set ::L {}
set ::on 0
debug set_watchpoint write_mem 0x9800 {} { if {$::on} { lappend ::L "[format %.7f [machine_info time]] $::wp_last_value" } }
dstep {[peek 0xC00F] == 50} { }
dpause 6
dstep 1 { key 8 0x01 0.2 }
dpause 4
dstep 1 { log "sccm=[peek 0xC37A] scc=[peek 0xC1FE] pg=[format %02X [peek 0xC1F4]]/[format %02X [peek 0xC1F5]] on=[peek 0xC0D0] fi=[peek 0xC37B]/[peek 0xC37C]"; set ::on 1 }
dpause 0.6
dstep 1 { set ::on 0; set fh [open "F:/MSX Projects/PMdev26/work/shots/t101.txt" w]; puts $fh [join $::L "\n"]; close $fh; exit }
drun
