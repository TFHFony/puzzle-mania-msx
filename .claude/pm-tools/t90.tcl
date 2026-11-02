# attract mode, tick, confetti:  DUMP=<prefix> openmsx -machine Philips_VG_8020 -cart PuzzleMania_EXTRAS_ASCII16.rom -romtype ASCII16 -script t90.tcl
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle on
set ::sfxn 0
debug set_watchpoint write_mem 0xC1F6 {} { if {[peek 0xC1F6] == 2} { incr ::sfxn } }
proc w90 {} {
  set s "att=[peek 0xC1F7] photo=[peek 0xC000] size=[peek 0xC001] trk=[peek 0xC0D1] done=[peek 0xC300][peek 0xC301][peek 0xC302][peek 0xC303][peek 0xC304][peek 0xC305][peek 0xC306][peek 0xC307][peek 0xC308]"
  if {![info exists ::lw] || $s ne $::lw} { log "$s sfx=$::sfxn"; set ::lw $s }
  after time 0.25 w90
}
w90
dstep {[peek 0xC00F] == 50} { log start }
dpause 8
dstep 1 { key 8 0x01 0.2 }
dpause 3
dstep 1 { shot 90_menu }
dstep {[peek 0xC1F7] == 1 && [peek 0xC0F0] >= 40} { shot 91_att; log "moves=[peek 0xC0F0]" }
dstep {[peek 0xC0D1] == 2 && [peek 0xC1F7] == 1} { }
dpause 0.8
dstep 1 { shot 92_win }
dpause 1.2
dstep 1 { shot 93_win }
dpause 1.5
dstep 1 { shot 94_win }
dstep {[peek 0xC1F7] == 0} { log "back in the menu" ; shot 95_menu }
dstep {[peek 0xC1F7] == 1} { log "second attract" }
dpause 2
dstep 1 { shot 96_att2 }
dpause 4
dstep 1 { key 8 0x01 0.3 }
dpause 3
dstep 1 { log "after key: att=[peek 0xC1F7]"; shot 97_after; exit }
drun
