set throttle off
set n 0
proc tick {} {
  global n
  set t [machine_info time]
  if {$t >= $n} {
    set f [open $::env(OUT) a]
    puts $f [format "%.1f r1=%02X vram1=%s pc=%04X" $t [debug read "VDP regs" 1] [debug read_block VRAM 0 8] [reg PC]]
    close $f
    incr n 2
  }
  if {$t > 50} { exit }
  after frame tick
}
after frame tick
