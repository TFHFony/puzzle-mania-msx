# dump the VRAM at every iteration of wipe_in (the FONY logo, first call): env OUT = dir, ADDR = address of wipe_in.l
set throttle off
set ::n 0
after time 60 { exit }
debug set_bp $::env(ADDR) {} {
  if {$::n < 14} {
    set f [open "$::env(OUT)/v[format %02d $::n].txt" w]
    set s ""
    for {set a 0} {$a < 0x1800} {incr a} { append s [format %02x [vpeek $a]] }
    puts $f $s
    set s ""
    for {set a 0x2000} {$a < 0x3800} {incr a} { append s [format %02x [vpeek $a]] }
    puts $f $s
    set s ""
    for {set a 0x1B00} {$a < 0x1B14} {incr a} { append s [format %02x [vpeek $a]] }
    puts $f $s
    puts $f "reg7 [format %02x [vdpreg 7]] reg1 [format %02x [vdpreg 1]]"
    close $f
  }
  incr ::n
  if {$::n == 16} { exit }
}
