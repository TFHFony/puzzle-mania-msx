# the title video: the bank in the window at 8000h (TVBANK + tv_f) against the ROM file, at several moments
set ::res {}
proc chk {} {
  debug break
  set f [peek 0xC1EF]
  set s ""
  foreach o {0 1 100 5000 16000 16383} { append s [peek [expr {0x8000+$o}]] " " }
  lappend ::res "tv_f=$f $s"
  debug cont
}
foreach t {12 20 30 40 45} { after time $t chk }
after time 46 { set fh [open "F:/MSX Projects/PMdev26/work/shots/hb.txt" w]; puts $fh [join $::res "\n"]; close $fh; exit }
set throttle off
