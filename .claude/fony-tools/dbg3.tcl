set throttle off
proc dump {} {
  set f [open "F:/MSX Projects/PMdev26/.claude/fony-tools/rec/vram.hex" w]
  for {set a 0} {$a < 0x6A00} {incr a 128} {
    set s ""
    for {set i 0} {$i < 128} {incr i} { append s [format %02x [debug read "physical VRAM" [expr {0x8000+$a+$i}]]] }
    puts $f $s
  }
  close $f
}
after time 7.0 dump
after time 7.5 exit
