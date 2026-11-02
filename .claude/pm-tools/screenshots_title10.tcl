# 10 screenshots of the title video (the PM logo with the clip in the letters), evenly spread over the video: DUMP=<prefix>
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle on
after time 300 { exit }
dstep {[peek 0xC00F] == 50} { poke 0xC1F9 0; log start }
dstep {[peek 0xC1F9] == 1} { log "title video" }
dpause 1.2
for {set i 0} {$i < 10} {incr i} {
  dstep 1 [list shot [format %02d [expr {$i + 1}]]]
  dpause 2.7
}
dstep 1 { exit }
drun
