# tiny driver: steps drun one after the other, each waits for its condition (polled every 20 ms of emulated time)
set throttle off
set frameskip 0
set ::steps {}
set ::cur 0
proc log {m} { set f [open "F:/MSX Projects/PMdev26/work/shots/log.txt" a]; puts $f "[format %.2f [machine_info time]] $m"; close $f }
proc key {row mask t} { keymatrixdown $row $mask; after time $t "keymatrixup $row $mask" }
proc shot {n} { screenshot "$::env(DUMP)-$n.png" }
proc dstep {cond script} { lappend ::steps [list $cond $script] }
proc wait_unused {sec} { dstep "\[expr {\[machine_info time\] >= \$::tw}\]" {} ; lset ::steps end 1 "" ; set i [expr {[llength $::steps]-1}]; lset ::steps $i 0 "expr {\[machine_info time\] >= \$::tw}" }
proc dpause {sec} { lappend ::steps [list "dpause" $sec] }
proc drun {} { if {[catch {drun1} err]} { log "ERR $err" } ; after time 0.02 drun }
proc drun1 {} {
  if {$::cur >= [llength $::steps]} { return }
  lassign [lindex $::steps $::cur] cond script
  if {$cond eq "dpause"} {
    if {![info exists ::pt]} { set ::pt [expr {[machine_info time] + $script}] }
    if {[machine_info time] >= $::pt} { unset ::pt; incr ::cur }
  } elseif {[uplevel #0 [list expr $cond]]} {
    uplevel #0 $script
    incr ::cur
  }
}
proc dwatch {} {
  set s "on=[peek 0xC0D0] trk=[peek 0xC0D1] gs=[peek 0xC0DF] gt=[peek 0xC0E4]"
  if {![info exists ::lastw] || $s ne $::lastw} { log $s; set ::lastw $s }
  after time 0.02 dwatch
}
