set throttle off
set n 0
proc tick {} {
  global n
  set t [machine_info time]
  if {$t >= $n} {
    set f [open $::env(OUT) a]
    puts $f [format "%.2f r1=%02X pc=%04X vram=%s" $t [debug read "VDP regs" 1] [reg PC] [debug read_block VRAM 0 12]]
    close $f
    set n [expr {$n + 2}]
  }
  if {$t >= 12 && $t < 12.1} { screenshot "$::env(OUT).png" }
  if {$t > 14} { exit }
  after frame tick
}
after frame tick
