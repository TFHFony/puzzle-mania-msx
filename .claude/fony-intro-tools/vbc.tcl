set throttle off
after time 9 { set f [open $::env(OUT) w]; puts $f "v_bc=[peek 0xC17F] v_msx=[peek 0xC1FC] RG7SAV=[peek 0xF3E6] RG8=[peek 0xFFE7]"; close $f; exit }
