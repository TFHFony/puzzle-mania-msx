# music at the title (video / photo) in the SCC version: PSG volume writes, SCC volume writes
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
set ::reg 0
set ::psg 0
set ::scc {}
set ::ph "video"
debug set_watchpoint write_io 0xA0 {} { set ::reg $::wp_last_value }
debug set_watchpoint write_io 0xA1 {} { if {$::reg >= 8 && $::reg <= 10 && $::wp_last_value != 0 && [peek 0xC1F7] == 0} { incr ::psg } }
debug set_watchpoint write_mem 0x988A {} { lappend ::scc "[format %.1f [machine_info time]]=$::wp_last_value" }
dstep {[peek 0xC00F] == 50} { }
dpause 25
dstep 1 { log "title video phase: psg nonzero volume writes so far=$::psg  tv_f=[peek 0xC1EF] sccm=[peek 0xC37A] mus_on=[peek 0xC0D0]"; set ::psg0 $::psg }
dstep {[peek 0xC1F9] == 0 && [peek 0xC0D1] == 0 && [peek 0xC0D0] == 1} { }
dpause 2
dstep 1 { log "after: psg=$::psg scc volume writes: [lrange $::scc end-8 end] mus_on=[peek 0xC0D0] trk=[peek 0xC0D1]"; exit }
drun
