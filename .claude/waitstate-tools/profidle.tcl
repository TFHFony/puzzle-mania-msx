set throttle off
set ::go 0
set ::cap 0
set ::n 0
set ::L {}
after time $::env(T0) { set ::go 1 }
debug set_bp 0xD300 {} {
  if {$::go} { incr ::n; if {$::n == 1} { set ::cap 1 }
    if {$::cap} { lappend ::L "M 0000 [format %.9f [machine_info time]]" }
    if {$::n == 3} { set f [open $::env(OUT) w]; puts $f [join $::L "\n"]; close $f; exit } }
}
foreach a $::env(ADDRS) { debug set_bp $a {} { if {$::cap} { lappend ::L "I [format %04X [reg PC]] [format %.9f [machine_info time]]" } } }
after time 200 { exit }
