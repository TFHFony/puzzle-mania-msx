set throttle off
set last -1
proc tick {} {
  global last
  set t [machine_info time]
  set r [debug read "VDP regs" 1]
  if {$r != $last} { set f [open $::env(OUT) a]; puts $f [format "%.3f R1=%02X wait=%d tvd=%d" $t $r [peek 0xC390] [peek 0xC391]]; close $f; set last $r }
  if {$t > 20} { exit }
  after frame tick
}
after frame tick
