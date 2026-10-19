# every action of the game: silent gaps of the music (ms) per action
source "F:/MSX Projects/PMdev26/.claude/pm-tools/lib.tcl"
set throttle off
set ::L {}
set ::on 0
set ::A {}
debug set_watchpoint write_io 0xA0 {} { if {$::on && $::wp_last_value == 8} { lappend ::L [machine_info time] } }
proc act {n} { lappend ::A "$n [format %.3f [machine_info time]]" }
dstep {[peek 0xC00F] == 50} { set ::on 1; act start }
dpause 5.5
dstep 1 { act title_space; key 8 0x01 0.2 }
dpause 3.5
dstep 1 { act carousel_right; key 8 0x80 0.15 }
dpause 1.5
dstep 1 { act carousel_right2; key 8 0x80 0.15 }
dpause 1.5
dstep 1 { act carousel_left; key 8 0x10 0.15 }
dpause 1.5
dstep 1 { act menu_down; key 8 0x40 0.15 }
dpause 1.5
dstep 1 { act help_open; key 3 0x20 0.3 }
dpause 2
dstep 1 { act help_page2; key 8 0x01 0.2 }
dpause 2
dstep 1 { act help_close; key 8 0x01 0.2 }
dpause 3
dstep 1 { act esc_credits; key 7 0x04 0.2 }
dpause 3
dstep 1 { act credits_back; key 8 0x01 0.2 }
dpause 3
dstep 1 { act pick_photo; key 8 0x01 0.2 }
dpause 3
dstep 1 { act size_move; key 8 0x80 0.15 }
dpause 1
dstep 1 { act size_L; key 4 0x02 0.15 }
dpause 1.5
dstep 1 { act size_C; key 3 0x01 0.15 }
dpause 1.5
dstep 1 { act start_puzzle; key 8 0x01 0.2 }
dpause 4.5
dstep 1 { act puzzle_move; key 8 0x20 0.15 }
dpause 1.5
dstep 1 { act puzzle_H; key 3 0x20 0.5 }
dpause 2.5
dstep 1 { act puzzle_esc; key 7 0x04 0.2 }
dpause 4
dstep 1 { set ::on 0; set f [open "F:/MSX Projects/PMdev26/work/psg70.txt" w]; puts $f [join $::L "\n"]; close $f; set f [open "F:/MSX Projects/PMdev26/work/act79.txt" w]; puts $f [join $::A "\n"]; close $f; exit }
drun
