set throttle off
proc key {row mask t0 dur} { after time $t0 "keymatrixdown $row $mask"; after time [expr {$t0 + $dur}] "keymatrixup $row $mask" }
proc snap {} {
  set f [open $::env(OUT) a]
  puts $f [format "%.2f k8=%02X t3=%d dk=%d dkey=%d pdir=%d rep=%d busy=%d on=%d moves=%d" [machine_info time] [peek 0xC0E0] [peek 0xC39B] [peek 0xC398] [peek 0xC39D] [peek 0xC003] [peek 0xC004] [peek 0xC148] [peek 0xC0D0] [peek 0xC0F0]]
  close $f
}
key 8 1 47 0.3
key 8 1 52 0.3
key 8 0x10 60 1.0
foreach t {59.9 60.1 60.2 60.3 60.5 60.8 61.2} { after time $t snap }
after time 62 { exit }
