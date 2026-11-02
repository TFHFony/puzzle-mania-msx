set throttle off
proc dump {} { set f [open "dbg.txt" a]; puts $f "t=[machine_info time] PC=[format %04X [reg PC]] B2=[reg B2] DE2=[reg DE2] HL=[format %04X [reg HL]] SP=[format %04X [reg SP]] tn=[peek 0xC000]"; close $f }
file delete dbg.txt
foreach t {8 10 12 14 20} { after time $t dump }
after time 21 exit
