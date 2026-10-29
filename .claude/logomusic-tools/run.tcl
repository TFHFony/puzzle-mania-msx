# plays the logo with the key KEY (1..4) and writes the start/end time of the video: OUT=<file> KEY=<n> SHOT=<prefix>
set throttle off
set frameskip 0
set key $::env(KEY)
set st 0
proc tick {} { if {[catch {tick2} e]} { set f [open err.txt a]; puts $f $e; close $f; exit }; after frame tick }
proc tick2 {} {
  global key st t0
  set t [machine_info time]
  if {$st == 0 && $t >= $::env(T0) && [debug read VRAM 1] == 80 && [debug read VRAM 2] == 77 && [debug read VRAM 4] == 76} {
    screenshot "$::env(SHOT)_menu.png"
    keymatrixdown 0 [expr {1 << $key}]
    set st 1; set t0 $t
  } elseif {$st == 1 && $t >= $t0 + 0.3} {
    keymatrixup 0 [expr {1 << $key}]
    set st 2
  } elseif {$st == 2 && $t >= $t0 + 5} {
    screenshot "$::env(SHOT)_play.png"
    set st 3
  } elseif {$st == 3 && [debug read "VDP regs" 1] == 0x50} {
    set f [open $::env(OUT) w]; puts $f "start $t0 end $t duration [expr {$t - $t0 - 0.3}]"; close $f
    exit
  } elseif {$t > 120} { exit }

}
after frame tick
