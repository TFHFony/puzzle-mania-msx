set throttle off
proc fl {m} { set f [open "F:/MSX Projects/PMdev26/.claude/fony-tools/rec/dbg2.txt" a]; puts $f $m; close $f }
set ::n 0
proc hit {name} { incr ::n; if {$::n < 80} { fl "$name t=[format %.3f [machine_info time]] a=[format %02x [reg A]] f=[format %02x [reg F]] c=[format %02x [reg C]] b=[format %02x [reg B]] v_i=[peek 0xc00e] van=[peek 0xc1e8]" } }
set cond {[peek 0x4776]==0xCD && [peek 0x4777]==0xE4}
foreach {addr name} {0x4795 key 0x47A9 joy 0x47AF cp28 0x47D5 nout 0x47E1 END 0x47DB nxt} {
  debug set_bp $addr $cond "hit $name"
}
after time 30 exit
