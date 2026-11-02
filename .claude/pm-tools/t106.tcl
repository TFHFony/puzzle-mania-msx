source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
dstep {[peek 0xC00F] == 50} { }
dstep {[peek 0xC1FD] == 1} { }
dpause 3
dpause 3
dstep 1 {
  set b [debug read_block "VDP palette" 0 32]
  binary scan $b c* l
  set s ""
  foreach x $l { append s [format %02X [expr {$x & 255}]] " " }
  set r ""; set rb [debug read_block "VDP regs" 0 28]; binary scan $rb c* rl; foreach x $rl { append r [format %02X [expr {$x & 255}]] " " }; set r "$r | "
  
  set vr ""
  foreach a {0 1 2 3 8 9 16 17 4096 4097 6144 6145 8192 8193} { append vr [format %02X [vpeek $a]] " " }
  log "pal: $s"
  log "vdpregs: $r"
  log "vram@0,1,2,3,8,9,10h,11h,1000h,1001h,1800h,1801h,2000h,2001h: $vr"
  log "v_pal=[peek 0xC1FD] msx=[peek 0xC1FC]"
  exit
}
drun
