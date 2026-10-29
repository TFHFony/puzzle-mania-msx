# profile of one idle menu frame: time at every instruction of the player prologue / epilogue and of the caller loop, from one mvsync_ call to the next
set throttle off
set ::go 0
set ::cap 0
set ::L {}
after time $::env(T0) { set ::go 1 }
debug set_bp 0xD300 {} {
  if {$::go == 1} { set ::go 2; set ::cap 1 } elseif {$::go == 2} { set ::cap 0; set ::go 3; lappend ::L "END [format %.9f [machine_info time]]"; set f [open $::env(OUT) w]; puts $f [join $::L "\n"]; close $f; exit }
}
foreach a $::env(ADDRS) { debug set_bp $a {} { if {$::cap} { lappend ::L "[format %04X [reg PC]] [format %.9f [machine_info time]]" } } }
after time 100 { exit }
