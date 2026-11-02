set throttle off
set ::fh [open $::env(OUT) w]
set ::last 0
set ::trail {}
# keep the last PCs that are in the overlay (4000h..7FFFh)
debug set_condition {[reg PC] >= 0x8000 && [reg PC] < 0xC000 && [machine_info time] > 6} {
  puts $::fh "in data: PC=[format %04X [reg PC]] SP=[format %04X [reg SP]] AF=[format %04X [reg AF]] BC=[format %04X [reg BC]] DE=[format %04X [reg DE]] HL=[format %04X [reg HL]] IX=[format %04X [reg IX]] IY=[format %04X [reg IY]] t=[machine_info time]"
  puts $::fh "stack: [debug read_block memory [expr {[reg SP]-8}] 16]"
  puts $::fh "trail: $::trail"
  close $::fh; exit
}
debug set_condition {[reg PC] >= 0x4000 && [reg PC] < 0x8000 && [machine_info time] > 6} {
  set ::trail [lrange [concat $::trail [format %04X [reg PC]]] end-5 end]
}
after time 20 { puts $::fh "timeout"; close $::fh; exit }
