set throttle off
set ::L {}
proc dump {tag} {
  set c {}; for {set a 0} {$a < 12} {incr a} { lappend c [format %02X [vpeek [expr {0x2000 + $a}]]] }
  set p {}; for {set a 0} {$a < 12} {incr a} { lappend p [format %02X [vpeek $a]] }
  set n {}; for {set a 0} {$a < 6} {incr a} { lappend n [format %02X [vpeek [expr {0x1800 + $a}]]] }
  set r {}; for {set a 0} {$a < 8} {incr a} { lappend r [format %02X [vdpreg $a]] }
  lappend ::L "[format %.3f [machine_info time]] $tag v_bc=[peek 0xC17F] col=$c pat=$p name=$n R0-7=$r"
}
debug set_bp 0x$::env(WC) {} { dump "wipe_clear start" }
debug set_bp 0x$::env(SC) {} { dump "start_col entry"; after time 0.5 { dump "0.5 s after start_col" } }
after time 9 { set f [open $::env(OUT) w]; puts $f [join $::L "\n"]; close $f; exit }
