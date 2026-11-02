source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
set ::n 0
proc chk {} {
  set b [debug read_block "VDP regs" 0 4]
  binary scan $b c* l
  set s ""
  foreach x $l { append s [format %02X [expr {$x & 255}]] " " }
  if {$s ne "02 40 06 FF " && [peek 0xC00F] == 50 && $::n < 6} { incr ::n; log "regs=$s v_pal=[peek 0xC1FD] pc=[format %04X [reg PC]] mus=[peek 0xC0D0] trk=[peek 0xC0D1] att=[peek 0xC1F7] tit=[peek 0xC1F9]" }
  after time 0.02 chk
}
dstep {[peek 0xC00F] == 50} { }
chk
after time 100 { exit }
drun
