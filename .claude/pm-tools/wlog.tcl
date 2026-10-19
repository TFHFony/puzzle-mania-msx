# logs the time of every write to the PSG ports A0 / A1 for 0.4 s (after 8 s) -> work/wlog.txt
set ::L {}
set ::on 0
proc rec {p} { if {$::on} { lappend ::L "$p $::wp_last_value [machine_info time]" } }
debug set_watchpoint write_io 0xA0 {} { rec 0 }
debug set_watchpoint write_io 0xA1 {} { rec 1 }
after time 8 { set ::on 1 }
after time 8.4 { set ::on 0; set f [open "F:/MSX Projects/PMdev26/work/wlog.txt" w]; puts $f [join $::L "\n"]; close $f; exit }
set throttle off
