set throttle off
set ::fh [open $::env(OUT) w]
proc lg {m} { puts $::fh "[format %.2f [machine_info time]] $m"; flush $::fh }
set ::reached 0
debug set_bp 0x$::env(ML) {} { if {!$::reached} { set ::reached 1; lg "mode_loop reached" } }
debug set_bp 0x$::env(S0) {} { lg "stub ovl_mm_init" }
debug set_bp 0x4000 {} { if {$::reached} { lg "bp 4000 PC=[format %04X [reg PC]] page1 slot=[get_selected_slot 1]" } }
proc skip {} { if {!$::reached} { keymatrixdown 8 1; after time 0.1 { keymatrixup 8 1 }; after time 0.7 skip } }
skip
set ::trail {}
debug set_condition {$::reached && [peek [reg PC]] == 0x76 && [reg PC] < 0xC000} {
  lg "HALT at PC=[format %04X [reg PC]] SP=[format %04X [reg SP]] AF=[format %04X [reg AF]] BC=[format %04X [reg BC]] DE=[format %04X [reg DE]] HL=[format %04X [reg HL]]"
  lg "stack: [debug read_block memory [reg SP] 8]"
  close $::fh; exit
}
after time 200 { lg timeout; close $::fh; exit }
