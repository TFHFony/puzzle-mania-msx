# boot test: SLTTBL[1] (FCC6h) is set to $::env(SLT) just before the game starts (INIT at 4020h); after 15 s: v_own, v_scc, v_sccm, PC, screenshot.  DUMP=prefix
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
debug set_bp 0x4020 {} {
  poke 0xFCC6 [expr {$::env(SLT)}]
  log "init: SLTTBL1 now [format %02X [peek 0xFCC6]] EXPTBL1 [format %02X [peek 0xFCC1]]"
}
after time 15 {
  log "t15: v_own=[format %02X [peek 0xC1F6]] v_scc=[peek 0xC1FE] v_sccm=[peek 0xC37A]  PC=[format %04X [reg PC]] hz=[peek 0xC00F] on=[peek 0xC0D0]"
  screenshot "$::env(DUMP)-boot.png"
  exit
}
