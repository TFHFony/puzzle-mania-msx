# jigsaw outro test: frames of the outro as screenshots and their times.  env: MODE=video|photo  OUT=dir (existing)  [FAST=1: the photo title waits only a few seconds]
set throttle [expr {[info exists ::env(THR)] ? "on" : "off"}]
set frameskip 0
set ::t0 0
set ::n 0
set ::L {}
proc lg {m} { lappend ::L "[format %.3f [machine_info time]] $m" }
set ::k 0
proc per {} { screenshot "$::env(OUT)/p[format %02d $::k].png"; incr ::k; after time $::env(PER) per }
if {[info exists ::env(PER)]} { after time [expr {[info exists ::env(T0)] ? $::env(T0) : 8}] per }
if {[info exists ::env(END)]} { after time $::env(END) { fin } }
proc fin {} { set f [open "$::env(OUT)/log.txt" w]; puts $f [join $::L "\n"]; close $f; exit }
after time 90 { lg "watchdog"; fin }
if {$::env(MODE) eq "photo"} { after time 6 { poke 0xC1F9 1 } }
debug set_bp 0x7F14 {} { screenshot "$::env(OUT)/start.png"; lg "ovl_jig start vbank=[expr {[peek 0xC040]+256*[peek 0xC041]}]"; set ::t0 [machine_info time] }
debug set_bp 0x47A8 {} { incr ::n; lg "frame $::n end"; screenshot "$::env(OUT)/f[format %03d $::n].png" }
debug set_bp 0x7F20 {} { set nz 0; set nc 0; for {set a 0} {$a < 6144} {incr a} { if {[vpeek $a] != 0} { incr nz }; if {[vpeek [expr {0x2000 + $a}]] != 0} { incr nc } }; lg "ovl_jig return carry=[expr {[reg F] & 1}] vram nonzero pat=$nz col=$nc"; after time [expr {[info exists ::env(EXTRA)] ? $::env(EXTRA) : 1.5}] fin }
