# title -> menu transition: late frames (sl = 0) and the frame times, PAL (hz 50) or NTSC (hz 60: env HZ)
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
set ::H {}
set ::go 0
debug set_watchpoint write_mem 0xC0FC {} { if {$::go} { lappend ::H "[format %.3f [machine_info time]] sl=$::wp_last_value qn=[peek 0xC15B] busy=[peek 0xC148] n=[peek 0xC0FD] sk=[peek 0xC142] hint=[peek 0xC1EB]" } }
dstep {[peek 0xC00F] == $::env(HZ)} { }
dpause 7
dstep 1 { set ::go 1; log "title: mus=[peek 0xC0D0]"; key 8 0x01 0.2 }
dpause 3
dstep 1 { set f [open "F:/MSX Projects/PMdev26/work/k2log.txt" w]; puts $f [join $::H "\n"]; close $f; exit }
drun
