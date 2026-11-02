source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
set ::L {}
debug set_watchpoint write_io {0x99 0x9A} {} {
  lappend ::L "[format %02X $::wp_last_address]:[format %02X $::wp_last_value]@[format %04X [reg PC]]"
  if {[llength $::L] > 160} { set ::L [lrange $::L end-120 end] }
}
proc chk {} {
  set b [debug read_block "VDP regs" 0 1]
  binary scan $b c l
  if {($l & 255) != 2 && [peek 0xC00F] == 50} {
    set fh [open "F:/MSX Projects/PMdev26/work/shots/t109.txt" w]
    puts $fh "v_pal=[peek 0xC1FD] pc=[format %04X [reg PC]]"
    puts $fh [join $::L " "]; close $fh; exit
  }
  after time 0.005 chk
}
dstep {[peek 0xC00F] == 50} { }
chk
drun
