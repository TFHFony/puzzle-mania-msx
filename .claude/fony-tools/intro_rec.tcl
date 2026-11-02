# records the intro of the game (FONY logo + jingle): REC=<avi> LOG=<palette log> openmsx -machine M -cart PuzzleMania_128MB.rom -romtype NEO-16 [-ext scc] -script intro_rec.tcl
set throttle on
set ::pal {}
proc fl {m} { set f [open $::env(LOG) a]; puts $f $m; close $f }
proc poll {} {
  if {[catch {
    set s ""
    for {set i 0} {$i < 32} {incr i} { append s [format %02x [debug read "VDP palette" $i]] }
    if {$s ne $::pal} { set ::pal $s; fl "[format %.3f [machine_info time]] r0=[format %02x [vdpreg 0]] r1=[format %02x [vdpreg 1]] r8=[format %02x [vdpreg 8]] r9=[format %02x [vdpreg 9]] $s" }
  } err]} { fl "ERR $err" }
  after time 0.02 poll
}
proc go {} {
  if {[catch {record start $::env(REC)} err]} { fl "REC ERR $err" }
  poll
}
after time 0.3 go
after time [expr {$::env(SECS)}] { catch {record stop}; exit }
