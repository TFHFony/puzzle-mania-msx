set throttle on
proc fl {m} { set f [open "F:/MSX Projects/PMdev26/.claude/fony-tools/rec/dbg.txt" a]; puts $f $m; close $f }
set ::last ""
proc snap {} {
  set pc [reg PC]
  if {1} {
    set s [format "pc=%04x v_i=%d" $pc [peek 0xc00e]]
    fl "t=[format %.3f [machine_info time]] $s sp=[format %04x [reg SP]] a=[format %02x [reg A]]"
  }
  after time 0.0005 snap
}
after time 5.69 snap
after time 5.95 exit
