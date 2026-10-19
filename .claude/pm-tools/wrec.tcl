# records 6 s of audio (after 8 s) and logs the PSG writes of that time: work/wrec.wav, work/wlog.txt
set ::L {}
set ::on 0
proc rec {p} { if {$::on} { lappend ::L "$p $::wp_last_value [machine_info time]" } }
debug set_watchpoint write_io 0xA0 {} { rec 0 }
debug set_watchpoint write_io 0xA1 {} { rec 1 }
after time 8 { set ::on 1; record start "F:/MSX Projects/PMdev26/work/wrec.wav" -audioonly }
after time 14 { set ::on 0; record stop; set f [open "F:/MSX Projects/PMdev26/work/wlog.txt" w]; puts $f [join $::L "\n"]; close $f; exit }
set throttle on
