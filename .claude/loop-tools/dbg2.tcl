set throttle off
proc w16 {a} { expr {[peek $a] + 256*[peek [expr {$a+1}]]} }
proc dump {} { set f [open "dbg2.txt" a]; puts $f "t=[format %.1f [machine_info time]] PC=[format %04X [reg PC]] tn=[peek 0xC002] DE=[format %04X [reg DE]] HL=[format %04X [reg HL]] SP=[format %04X [reg SP]]"; close $f }
file delete dbg2.txt
foreach t {20 25 30 35 45} { after time $t dump }
after time 46 exit
