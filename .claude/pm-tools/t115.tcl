source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
set ::o {}
set ::n 0
debug set_watchpoint write_mem 0xC0E0 {} { if {$::n < 24} { incr ::n; lappend ::o "t=[format %.3f [machine_info time]] k8<-[format %02X $::wp_last_value] pc=[format %04X [reg PC]] joy=[format %02X [peek 0xC1EE]] jc=[format %02X [peek 0xC37D]]" } }
dstep {[peek 0xC00F] == 50} { }
dpause 7
dstep 1 { set ::n 0 }
dpause 0.3
dstep 1 { set fh [open "F:/MSX Projects/PMdev26/work/shots/t115.txt" w]; puts $fh [join $::o "\n"]; close $fh; exit }
drun
