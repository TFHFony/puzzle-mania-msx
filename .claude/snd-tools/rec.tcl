set throttle off
debug set_bp 0x7F2A {} { record start "$::env(OUT)" -audioonly }
debug set_bp 0x7F36 {} { record stop; after time 0.2 exit }
after time 60 { exit }
