source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
set ::o {}
proc snap {} { lappend ::o "t=[format %.0f [machine_info time]] pc=[format %04X [reg PC]] att=[peek 0xC1F7] trk=[peek 0xC0D1] on=[peek 0xC0D0] sccm=[peek 0xC37A] v_pal=[peek 0xC1FD] done=[peek 0xC0E7]"; after time 10 snap }
snap
dstep {[peek 0xC00F] == 50} { }
dpause 6
dstep 1 { key 8 0x01 0.2 }
after time 150 { set fh [open "F:/MSX Projects/PMdev26/work/shots/t102.txt" w]; puts $fh [join $::o "\n"]; close $fh; exit }
drun
