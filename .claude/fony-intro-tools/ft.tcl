# the FONY film and the dreun in the game: log start/end (carry) of ovl_fony and ovl_snd, optional key press, optional wait-state loop, screenshots
set throttle off
set ::L {}
proc lg {m} { lappend ::L "[format %.3f [machine_info time]] $m" }
debug set_bp 0x$::env(F0) {} { lg "film start"; if {[info exists ::env(WAIT)]} { poke 0xC391 1 }; if {[info exists ::env(KEYAT)]} { after time $::env(KEYAT) { keymatrixdown 8 1; after time 0.15 { keymatrixup 8 1 } } } }
debug set_bp 0x$::env(F1) {} { lg "film end carry=[expr {[reg AF] & 1}] v_tvd=[peek 0xC391]" }
debug set_bp 0x$::env(S0) {} { lg "snd start C=[format %02X [reg C]]"; if {[reg C] >= 128} { after time 0.3 { screenshot "$::env(OUT)/xxxl.png" } } }
debug set_bp 0x$::env(S1) {} { lg "snd end carry=[expr {[reg AF] & 1}]" }
if {[info exists ::env(SHOTAT)]} { after time $::env(SHOTAT) { screenshot "$::env(OUT)/film.png" } }
after time $::env(END) { set f [open "$::env(OUT)/log.txt" w]; puts $f [join $::L "\n"]; close $f; exit }
