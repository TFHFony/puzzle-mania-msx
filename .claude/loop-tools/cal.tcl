set throttle off
if {[info exists ::env(ZF)]} { set z80_freq_locked false; set z80_freq $::env(ZF) }
proc w16 {a} { expr {[peek $a] + 256*[peek [expr {$a+1}]]} }
proc dump {tag} {
  set f [open "$::env(OUT)" a]
  puts $f "$tag t=[format %.2f [machine_info time]] f1=[w16 0xEF00] f2=[w16 0xEF02] n1=[w16 0xEF04] n2=[w16 0xEF06] x=[w16 0xEF08] fs=[w16 0xEF0A] ok=[peek 0xEF0C] r=[w16 0xEF0E] tvc=[peek 0xC1E8] tvi=[peek 0xC1E9] hz=[peek 0xC00F]"
  close $f }
file delete $::env(OUT)
foreach t $::env(TS) { after time $t "dump t$t" }
if {[info exists ::env(SHOT)]} { after time $::env(SHOT) { screenshot "$::env(OUT).png" } }
after time [expr {[lindex $::env(TS) end] + 1}] exit
