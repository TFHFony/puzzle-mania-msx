# functional test of the derived keys: SELECT in the menu toggles 50/60 Hz, SPACE picks the photo, SPACE the size, arrow keys move tiles
set throttle off
proc key {row mask t0 dur} { after time $t0 "keymatrixdown $row $mask"; after time [expr {$t0 + $dur}] "keymatrixup $row $mask" }
proc lg {m} { set f [open $::env(OUT) a]; puts $f "[format %.2f [machine_info time]] $m"; close $f }
after time 44 { lg "menu: hz=[peek 0xC00F] sel=[peek 0xC002]" }
key 7 0x40 45 0.3
after time 46 { lg "after SELECT: hz=[peek 0xC00F]" }
key 8 1 47 0.3
after time 50 { lg "after SPACE: size menu? track=[peek 0xC0D1] photo=[peek 0xC000]" }
key 8 1 52 0.3
after time 58 { lg "puzzle: size=[peek 0xC001] moves=[peek 0xC0F0]" }
set t 60
foreach k {0x10 0x20 0x80 0x40 0x10 0x20 0x80 0x40 0x10 0x20 0x80 0x40} { key 8 $k $t 0.12; set t [expr {$t + 0.6}] }
after time 70 { lg "after arrows: moves=[peek 0xC0F0] hz=[peek 0xC00F]"; exit }
after time 100 { exit }
