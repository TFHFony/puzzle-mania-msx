# packed clip frames: attract mode plays a clip; log bank/pointer and take screenshots
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
set ::n 0
proc w130 {} {
  set vl [expr {[peek 0xC042] + 256*[peek 0xC043]}]
  set vb [expr {[peek 0xC040] + 256*[peek 0xC041]}]
  set vp [expr {[peek 0xC04A] + 256*[peek 0xC04B]}]
  if {[peek 0xC1F7] == 1 && $::pz == 1 && $vl > 0 && $vl < 2000 && $vp >= 0x8000 && $vp < 0xC000} {
    if {![info exists ::t0]} { set ::t0 [machine_info time] }
    if {$vl < 200 && [machine_info time] - $::t0 >= 0.5 * $::n} { set h 0; for {set a 0x1000} {$a < 0x1800} {incr a 7} { set h [expr {($h*31 + [vpeek $a]) & 0xFFFFFF}] }; log "clip vl=$vl vp=[format %04X $vp] hash=$h"; incr ::n } elseif {$vl >= 200} { set ::t0 [machine_info time] }
  }
  after time 0.1 w130
}
set ::pz 0
w130
dstep {[peek 0xC00F] == 50} { }
dpause 8
dstep 1 { key 8 0x01 0.2; log "SPACE pressed" }
dstep {[peek 0xC1F7] == 1 && [peek 0xC0F0] >= 40} { log "puzzle"; set ::pz 1 }
dstep {[peek 0xC1F7] == 0} { log "back"; exit }
drun
