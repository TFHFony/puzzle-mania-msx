# who queues jobs for the memory bank (q_bank = MEMB) after the memory win? log jq_put calls (caller, dest, bank, queue length) from win_go on
set throttle off
set ::choice 0
set ::after 0
proc key {row mask} { keymatrixdown $row $mask; after time 0.12 [list keymatrixup $row $mask] }
proc skip {} { if {!$::choice} { key 8 1; after time 0.7 skip } }
set ::fh [open $::env(OUT) w]
proc lg {m} { puts $::fh "[format %.2f [machine_info time]] $m"; flush $::fh }
debug set_bp 0x$::env(ML) {} { set ::choice 1 }
debug set_bp 0x$::env(WIN) {} { set ::after 1; lg "win_go qn=[peek 0xC15B] go=[peek 0xC15F]" }
debug set_bp 0x$::env(JQ) {} { if {$::after} { set sp [reg SP]; lg [format "jq_put caller=%04X DE=%04X bank=%d qn=%d" [expr {[peek16 $sp]}] [reg DE] [peek16 0xC1E6] [peek 0xC15B]] } }
debug set_bp 0x$::env(JF) {} { if {$::after} { lg [format "job_flush caller=%04X qn=%d" [peek16 [reg SP]] [peek 0xC15B]] } }
debug set_bp 0x$::env(JR) {} { if {$::after} { lg [format "job_reset caller=%04X qn=%d" [peek16 [reg SP]] [peek 0xC15B]] } }
debug set_bp 0x$::env(MJ) {} { lg [format "mem_jobs m_jn=%d" [peek 0xC082]] }
skip
after time $::env(END) { lg " end"; close $::fh; exit }
