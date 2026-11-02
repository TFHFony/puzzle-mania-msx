# per frame log of the player in the puzzle: time, busy level, samples played, samples skipped, queue length (written at the entry of mvsync, so it describes the frame that has just ended)
# env: MODE=manual|attract  SIZE=3..6  CTL=0|1  OUT=file  [HOLD=1: also a held key]
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
set ::H {}
set ::on 0
set ::MODE $::env(MODE)
debug set_watchpoint write_mem 0xC0FC {} { if {$::on} { lappend ::H "[format %.4f [machine_info time]] [peek 0xC148] [peek 0xC0FD] [peek 0xC142] [peek 0xC15B]" } }
set ::P {}
proc setup_prof {} {
  set ::rets {}
  for {set a 0xD300} {$a < 0xF300} {incr a} { if {[peek $a] == 0xE1 && [peek [expr {$a+1}]] == 0xD1 && [peek [expr {$a+2}]] == 0xC1 && [peek [expr {$a+3}]] == 0xC9} { lappend ::rets [expr {$a+3}] } }
  log "ret candidates $::rets"
  foreach r $::rets { debug set_bp $r {} { if {$::on} { lappend ::P "R [format %.7f [machine_info time]] [format %04X [expr {[peek [reg SP]] + 256*[peek [expr {[reg SP]+1}]]}]] [peek 0xC148] [peek 0xC15B]" } } }
  if {[info exists ::env(PCS)]} { foreach a $::env(PCS) { debug set_bp $a {} "if {\$::on} { lappend ::P \"P \[format %.7f \[machine_info time\]\] [format %04X $a]\" }" } }
  debug set_bp 0xD300 {} { if {$::on} { lappend ::P "I [format %.7f [machine_info time]] [format %04X [expr {[peek [reg SP]] + 256*[peek [expr {[reg SP]+1}]]}]]" } }
}
proc save {} {
  if {[llength $::P]} { set f [open "$::env(OUT).prof" w]; puts $f [join $::P "
"]; close $f }
 catch { screenshot "$::env(OUT).png" }; set f [open $::env(OUT) w]; puts $f [join $::H "\n"]; puts $f "moves [expr {[peek 0xC0F0]+256*[peek 0xC0F1]}] size [peek 0xC001] n2 [peek 0xC024] ctl [peek 0xC01A]"; close $f }
set ::tstart 0
proc setk {} { if {[info exists ::env(KC)]} { poke 0xC16F $::env(KC) }; if {[info exists ::env(KB)]} { poke 0xC14F $::env(KB) } }
after time 100 { log "watchdog: stuck at step $::cur"; save; exit }
proc tick {} { log "st cur=$::cur hz=[peek 0xC00F] size=[peek 0xC001] n2=[peek 0xC024] trk=[peek 0xC0D1] gs=[peek 0xC0DF] att=[peek 0xC1F7]"; after time 5 tick }
after time 5 tick
if {$::MODE eq "attract"} {
  dstep {[peek 0xC00F] == 50 || [peek 0xC00F] == 60} { }
  dstep {[peek 0xC1F7] == 1 && [peek 0xC0D0] == 1 && [peek 0xC0D1] == 1} { }
  dpause 2.5
  dstep 1 { setk; set ::on 1; set ::tstart [machine_info time]; log "attract sz=[peek 0xC380] size=[peek 0xC001]" }
  dstep {[machine_info time] - $::tstart > 30 || [peek 0xC1F7] == 0} { set ::on 0; save; exit }
} else {
  dstep {[peek 0xC00F] == 50 || [peek 0xC00F] == 60} { }
  dpause 5.5
  dstep 1 { key 8 0x01 0.2 }
  dpause 3.5
  dstep 1 { key 8 0x01 0.2 }
  dpause 3
  if {$::env(SIZE) == 4 || $::env(SIZE) == 6} { dstep 1 { key 8 0x80 0.15 }; dpause 0.6 }
  if {$::env(SIZE) >= 5} { dstep 1 { key 8 0x40 0.15 }; dpause 0.6 }
  dstep 1 { key 8 0x01 0.2 }
  dstep {[peek 0xC0D1] == 1 && [peek 0xC0DF] == 0 && [peek 0xC024] == $::env(SIZE) * $::env(SIZE)} { log "puzzle n2=[peek 0xC024]" }
  dpause 2.5
  dstep 1 { poke 0xC01A $::env(CTL); setk }
  dpause 1
  dstep 1 { if {[info exists ::env(PROF)]} { setup_prof }; set ::on 1 }
  dpause 1
  set dirs {0x20 0x10 0x40 0x80 0x80 0x40 0x10 0x20}
  for {set i 0} {$i < 24} {incr i} {
    set d [lindex $dirs [expr {$i % 8}]]
    dstep 1 "key 8 $d 0.12"
    dpause 0.6
    if {$::env(CTL) == 1} { dstep 1 { key 8 0x01 0.12 }; dpause 0.6 }
  }
  if {[info exists ::env(HOLD)]} {
    dstep 1 { keymatrixdown 8 0x40 }
    dpause 1.6
    dstep 1 { keymatrixup 8 0x40 }
    dpause 1
    dstep 1 { keymatrixdown 8 0x20 }
    dpause 1.6
    dstep 1 { keymatrixup 8 0x20 }
    dpause 1
  }
  if {[info exists ::env(HINT)]} {
    dstep 1 { key 5 0x02 0.15 }
    dpause 3
    dstep 1 { key 5 0x02 0.15 }
    dpause 3
  }
  dstep 1 { set ::on 0; save; exit }
}
drun
