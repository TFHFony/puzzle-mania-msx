# records the first seconds of the v1.04 disk: AVI (zmbv + pcm) + a log of every palette change with the emulated time
set throttle on
set ::pal {}
set ::t0 0
proc fl {m} { set f [open "F:/MSX Projects/PMdev26/.claude/fony-tools/rec/pal.log" a]; puts $f $m; close $f }
proc poll {} {
  if {[catch {
    set s ""
    for {set i 0} {$i < 32} {incr i} { append s [format %02x [debug read "VDP palette" $i]] }
    if {$s ne $::pal} { set ::pal $s; fl "[format %.3f [expr {[machine_info time]-$::t0}]] r0=[format %02x [vdpreg 0]] r1=[format %02x [vdpreg 1]] $s" }
  } err]} { fl "ERR $err" }
  after time 0.02 poll
}
proc go {} {
  if {[catch {record start "F:/MSX Projects/PMdev26/.claude/fony-tools/rec/disk.avi"} err]} { fl "REC ERR $err" }
  set ::t0 0
  poll
}
after time 22 go
after time 40 { catch {record stop}; exit }
