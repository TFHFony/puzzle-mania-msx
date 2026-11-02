# (PHOTO=<0..9> the photo to solve, default 9; the music of the title photo plays 30 s at the end)
# full run: FONY logo, title video with its fade, menu, attract mode (photo 10 = STEF-1, 4x4), the clip, then the title photo.
# REC=<file.avi> openmsx -machine M -cart PuzzleMania_128MB.rom -romtype NEO-16 -ext scc -script stef_attract.tcl
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle on
after time 800 { exit }
dstep {[peek 0xC00F] == 50 || [peek 0xC00F] == 60} { set ph 9; if {[info exists ::env(PHOTO)]} {set ph $::env(PHOTO)}; for {set i 0} {$i < 10} {incr i} {poke [expr 0xC300 + $i] [expr {$i != $ph}]}; record start $::env(REC); log "recording; sccm=[peek 0xC37A] msx=[peek 0xC1FC]" }
dstep {[peek 0xC1F7] == 1} { poke 0xC380 4; log "attract on" }
dstep {[peek 0xC1F7] == 0} { log "attract over" }
dpause 30
dstep 1 { record stop; log "stopped"; exit }
drun
