# logs the time and PC of every PSG volume write (A1h) / SCC frequency write (9880h) of the jingle player
# env: MODE (psg|scc), OUT (file), SEC (emulated seconds to log)
set ::L {}
set kind $::env(MODE)
set sec $::env(SEC)
set throttle off
if {$kind eq "psg"} {
    debug set_watchpoint write_io 0xA1 {} { lappend ::L "[format %.8f [machine_info time]] [reg PC]" }
} else {
    debug set_watchpoint write_mem 0x9880 {} { lappend ::L "[format %.8f [machine_info time]] [reg PC]" }
}
after time $sec { set fh [open $::env(OUT) w]; puts $fh [join $::L "\n"]; close $fh; exit }
