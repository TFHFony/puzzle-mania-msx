# the attract mode solves a puzzle: log the jingle of the win (entry / return of the stub) and take screenshots afterwards.  env: OUT (dir), PHOTO
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
set ::L {}
proc lg {m} { lappend ::L "[format %.3f [machine_info time]] $m" }
set ::cnt 0
debug set_bp 0x7F2A {} { incr ::cnt; lg "jingle $::cnt start C=[format %02X [reg C]] v_sccm=[peek 0xC37A]" }
debug set_bp 0x7F36 {} { lg "jingle end carry=[expr {[reg AF] & 1}]"; set ::te [machine_info time] }
set ::sh 0
proc shots {} {
  if {[info exists ::te]} {
    foreach d {1 3 6} { if {[machine_info time] >= $::te + $d && $::sh < [expr {[lsearch {1 3 6} $d] + 1}]} { screenshot "$::env(OUT)/w$d.png"; incr ::sh; lg "shot $d" } }
  }
  after time 0.1 shots
}
after time 0.5 shots
after time 400 { set f [open "$::env(OUT)/log.txt" w]; puts $f [join $::L "\n"]; close $f; exit }
dstep {[peek 0xC00F] == 50 || [peek 0xC00F] == 60} { set ph 9; if {[info exists ::env(PHOTO)]} {set ph $::env(PHOTO)}; for {set i 0} {$i < 10} {incr i} {poke [expr 0xC300 + $i] [expr {$i != $ph}]} }
dstep {[peek 0xC1F7] == 1} { poke 0xC380 3; lg "attract on"; unset -nocomplain ::te; set ::sh 0 }
dstep {[info exists ::sh] && $::sh >= 3} { set f [open "$::env(OUT)/log.txt" w]; puts $f [join $::L "\n"]; close $f; exit }
drun
