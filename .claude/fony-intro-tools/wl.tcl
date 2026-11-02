set throttle off
set ::L {}
debug set_bp 0x000049B0 {} {
  set rows {}
  for {set r 0} {$r < 24} {incr r} { lappend rows [format %02X [vpeek [expr {0x2000 + $r*256}]]] }
  lappend ::L "[format %.3f [machine_info time]] i=[peek 0xC00E] colrow0..23=$rows"
}
after time 9 { set f [open $::env(OUT) w]; puts $f [join $::L "\n"]; close $f; exit }
