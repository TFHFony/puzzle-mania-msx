# per frame of the puzzle in the attract mode (mvsync_ calls): time, mus_sk (skipped samples of the frame being played next), mus_n, busy level (mus_pl), queue length (j_qn)
set throttle off
set ::go 0
set ::L {}
after time 1 { }
proc chk {} {
  if {!$::go && [peek 0xC1F7] == 1 && [peek 0xC001] != 0 && [peek 0xC0D1] == 1 && [peek 0xC0DF] == 0} { set ::go 1; set ::t0 [machine_info time] }
  after time 0.02 chk
}
after time 0.1 chk
debug set_bp 0xD300 {} { if {$::go} { lappend ::L "[format %.7f [machine_info time]] [peek 0xC142] [peek 0xC0FD] [peek 0xC1ED] [peek 0xC15B] [peek 0xC1F8]"; if {[machine_info time] > $::t0 + 12} { set f [open $::env(OUT) w]; puts $f [join $::L "\n"]; close $f; exit } } }
after time 200 { exit }
