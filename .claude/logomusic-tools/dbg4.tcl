set throttle off
proc tick {} {
  set t [machine_info time]
  if {$t >= 12} {
    set f [open $::env(OUT) w]
    catch {
      set s ""; for {set i 0} {$i < 28} {incr i} {append s [format "%02X " [debug read "VDP regs" $i]]}
      puts $f $s
      puts $f "pal: [palette]"
    } e
    puts $f "err: $e"
    close $f
    exit
  }
  after frame tick
}
after frame tick
