set throttle off
set n 0
set pressed 0
proc tick {} {
  global n pressed
  set t [machine_info time]
  if {!$pressed && $t >= 8} { keymatrixdown 0 8; set pressed 1; set tp $t }
  if {$pressed && $t >= 8.5 && $pressed == 1} { keymatrixup 0 8; set pressed 2 }
  if {$t >= $n} {
    set f [open $::env(OUT) a]
    puts $f [format "%.2f r1=%02X pc=%04X sp=%04X" $t [debug read "VDP regs" 1] [reg PC] [reg SP]]
    close $f
    set n [expr {$n + 0.25}]
  }
  if {$t > 14} { exit }
  after frame tick
}
after frame tick
