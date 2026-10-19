after time 9 {
  set f [open "F:/MSX Projects/PMdev26/work/dbg.txt" w]
  set bad 0
  for {set r 0} {$r < 4} {incr r} { for {set k 0} {$k < 80} {incr k} {
    set exp [peek [expr {0x4100 + 256*$r + $k}]]
    set got [vpeek [expr {0x1400 + 256*$r + $k}]]
    set gotc [vpeek [expr {0x3400 + 256*$r + $k}]]
    if {$exp != $got || $exp != $gotc} { incr bad; if {$bad < 6} { puts $f "r=$r k=$k exp=$exp got=$got colour=$gotc" } }
  } }
  set zbad 0
  for {set r 0} {$r < 4} {incr r} { for {set k 0} {$k < 80} {incr k} { if {[vpeek [expr {0x0C00 + 256*$r + $k}]] != 0} { incr zbad } } }
  puts $f "pattern/colour mismatches: $bad, zero rows mismatches: $zbad (qn=[peek 0xC15B])"
  # the byte after each run must be untouched (not the code byte)
  puts $f "after run: [vpeek 0x1450] [vpeek 0x1550]"
  close $f; exit }
set throttle off
