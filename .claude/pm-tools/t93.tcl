# game work between the calls of mvsync during the moves of the attract mode -> work/shots/t93.txt
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
set ::ev {}
set ::on 0
set ::seen {}
debug set_bp 0xD300 {} {
  if {$::on} { lappend ::ev "in [format %.6f [machine_info time]] [peek 0xC0F0]" }
  set r [peek16 [reg SP]]
  if {[lsearch $::seen $r] < 0} { lappend ::seen $r; debug set_bp $r {} { if {$::on} { lappend ::ev "out [format %.6f [machine_info time]] [peek 0xC0F0]" } } }
}
foreach {n a} {do_move 0x5ED3 domove 0x5A09 domove_ok 0x5A3C nh 0x5EE4 job_room 0x6382 job_move 0x65B8 put_tile 0x6500 put_blank 0x6566 cnt 0x5F17 posidx 0x5A91 solved 0x5ADE} {
  debug set_bp $a {} [list if {$::on} [list lappend ::ev "$n [format %.6f [machine_info time]] 0"]]
}
dstep {[peek 0xC00F] == 50} { }
dpause 8
dstep 1 { key 8 0x01 0.2 }
dstep {[peek 0xC1F7] == 1 && [peek 0xC0F0] >= 30} { set ::on 1 }
dstep {[peek 0xC0F0] >= 34} { set ::on 0; set f [open "F:/MSX Projects/PMdev26/work/shots/t93.txt" w]; puts $f [join $::ev "\n"]; puts $f "seen $::seen"; close $f; exit }
drun
