set throttle off
set ::t0 0; set ::n 0
debug set_bp 0x42CD {} { set ::t0 [machine_info time] }
debug set_bp 0x44C6 {} { set f [open "F:/MSX Projects/PMdev26/.claude/loop-tools/tn.txt" a]; puts $f [format "%.1f" [expr {([machine_info time]-$::t0)*3579545.4545}]]; close $f }
after time 11 exit
