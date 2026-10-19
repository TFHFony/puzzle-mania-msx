# logs the PSG register selects (A0) and the VDP writes (98/99) for 0.5 s (after 8 s) -> work/wlog2.txt
set ::L {}
set ::on 0
proc rec {p} { if {$::on} { lappend ::L "$p $::wp_last_value [machine_info time]" } }
debug set_watchpoint write_io 0xA0 {} { rec A0 }
debug set_watchpoint write_io 0x98 {} { rec 98 }
debug set_watchpoint write_io 0x99 {} { rec 99 }
after time 8 { set ::on 1 }
after time 8.5 { set ::on 0; set f [open "F:/MSX Projects/PMdev26/work/wlog2.txt" w]; puts $f [join $::L "\n"]; close $f; exit }
set throttle off
