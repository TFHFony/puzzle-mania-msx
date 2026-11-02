# memory game test: skip to the choice screen, choose memory, play all the pairs (one wrong try first), log; screenshots in OUT
set throttle off
set ::L {}
proc lg {m} { lappend ::L "[format %.2f [machine_info time]] $m"; set f [open "$::env(OUT)/log.txt" a]; puts $f "[format %.2f [machine_info time]] $m"; close $f }
set ::reached 0
set ::cx 0; set ::cy 0
proc shot {name} { set ::sv [set ::throttle]; set ::throttle on; after time 0.6 [list shot2 $name] }
proc shot2 {name} { screenshot "$::env(OUT)/$name.png"; set ::throttle off; lg "shot $name" }
set ::mlc 0
debug set_bp 0x$::env(ML) {} { incr ::mlc; if {!$::reached} { set ::reached 1; lg "choice screen"; after time 0.5 choice } else { lg "mode_loop again (hit $::mlc)" } }
debug set_bp 0x$::env(WIN) {} { lg "win called, moves=[expr {[peek 0xC12E] + 256*[peek 0xC12F]}] photo=[peek 0xC00D]"; after time 6 { shot win } ; after time 9 { shot win2 } ; after time 14 { skipvid } }
proc skipvid {} { keymatrixdown 8 1; after time 0.1 { keymatrixup 8 1 }; after time 1.0 skipvid }
proc skip {} { if {!$::reached} { keymatrixdown 8 1; after time 0.1 { keymatrixup 8 1 }; after time 0.7 skip } }
skip
proc fin {} { set f [open "$::env(OUT)/log.txt" w]; puts $f [join $::L "\n"]; close $f; exit }
after time 120 fin
# a queue of key actions
set ::Q {}
proc qrun {} {
  if {[llength $::Q] == 0} { return }
  set a [lindex $::Q 0]; set ::Q [lrange $::Q 1 end]
  lassign $a kind arg
  if {$kind eq "key"} { keymatrixdown 8 $arg; after time 0.07 "keymatrixup 8 $arg; after time 0.17 {qlog; qrun}" } \
  elseif {$kind eq "shot"} { shot $arg; after time 1.3 qrun } \
  elseif {$kind eq "wait"} { after time $arg qrun } \
  elseif {$kind eq "call"} { eval $arg; after time 0.05 qrun }
}
proc qlog {} { lg "cur=([peek 0xC128],[peek 0xC129]) sim=($::cx,$::cy) f1=[peek 0xC12A] f2=[peek 0xC12B] wait=[peek 0xC12C] pairs=[peek 0xC12D] moves=[peek 0xC12E]" }
proc press {mask} { lappend ::Q [list key $mask] }
proc goto {idx} {
  set tx [expr {$idx % 5}]; set ty [expr {$idx / 5}]
  while {$::cx != $tx} { press 128; set ::cx [expr {($::cx + 1) % 5}] }
  while {$::cy != $ty} { press 64; set ::cy [expr {($::cy + 1) % 4}] }
}
proc choice {} {
  lappend ::Q [list shot choice]
  press 128
  lappend ::Q [list shot choice_memory]
  press 1
  lappend ::Q [list wait 1.0]
  lappend ::Q [list shot board]
  lappend ::Q [list call plan]
  qrun
}
proc plan {} {
  set pic {}
  for {set i 0} {$i < 20} {incr i} { lappend pic [peek [expr {0xC100 + $i}]] }
  lg "board: $pic"
  set ::cx [peek 0xC128]; set ::cy [peek 0xC129]
  # a wrong try first
  set a 0; set b -1
  for {set i 1} {$i < 20} {incr i} { if {[lindex $pic $i] != [lindex $pic 0]} { set b $i; break } }
  goto $a; press 1; goto $b; press 1
  lappend ::Q [list shot wrong]
  lappend ::Q [list wait 2.0]
  lappend ::Q [list shot after_wrong]
  set done {}
  for {set i 0} {$i < 20} {incr i} {
    set p [lindex $pic $i]
    if {[lsearch $done $p] >= 0} { continue }
    lappend done $p
    set j -1
    for {set k [expr {$i+1}]} {$k < 20} {incr k} { if {[lindex $pic $k] == $p} { set j $k; break } }
    goto $i; press 1; goto $j; press 1
    if {[llength $done] == 5} { lappend ::Q [list shot half] }
  }
}
