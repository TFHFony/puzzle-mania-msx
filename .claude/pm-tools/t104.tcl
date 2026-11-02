# the MSX2 palette: v_pal (C1FD) and the palette registers of the VDP at every change, through the whole attract cycle
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
set ::last -1
proc w104 {} {
  set p [peek 0xC1FD]
  if {$p != $::last} {
    set ::last $p
    set b [debug read_block "VDP palette" 0 32]
    binary scan $b c* l
    set s ""
    foreach x [lrange $l 0 7] { append s [format %02X [expr {$x & 255}]] " " }
    log "v_pal=$p msx=[peek 0xC1FC] att=[peek 0xC1F7] photo=[peek 0xC000] pb=[expr {[peek 0xC1FA]+256*[peek 0xC1FB]}] vdp_pal=$s"
  }
  after time 0.05 w104
}
w104
after time 260 { exit }
