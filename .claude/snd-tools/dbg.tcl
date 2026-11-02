set throttle off
after time $::env(SEC) {
  set fh [open $::env(OUT) w]
  puts $fh "PC [format %04X [reg PC]] SP [format %04X [reg SP]] AF [format %04X [reg AF]] BC [format %04X [reg BC]] DE [format %04X [reg DE]] HL [format %04X [reg HL]] IX [format %04X [reg IX]] IY [format %04X [reg IY]] IFF [reg IFF]"
  puts $fh "slots [get_selected_slot 0] [get_selected_slot 1] [get_selected_slot 2] [get_selected_slot 3]"
  puts $fh "mem at PC: [debug read_block memory [reg PC] 8]"
  close $fh; exit
}
