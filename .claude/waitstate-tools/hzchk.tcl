set throttle off
proc snap {} {
  set f [open $::env(OUT) a]
  puts $f [format "%.2f hz=%d k7=%02X sel_prev=%02X mus_sel=%d on=%d" [machine_info time] [peek 0xC00F] [peek 0xC0E1] [peek 0xC383] [peek 0xC397] [peek 0xC0D0]]
  close $f
}
foreach t {6 10 20 30 40 44} { after time $t snap }
after time 45 { exit }
