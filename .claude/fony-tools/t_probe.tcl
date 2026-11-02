set f [open "F:/MSX Projects/PMdev26/.claude/fony-tools/rec/probe.txt" w]
puts $f "start"
catch {puts $f "time [machine_info time]"} e; puts $f $e
catch {puts $f "pal [debug read {VDP palette} 3]"} e; puts $f $e
catch {puts $f "reg [vdpreg 0]"} e; puts $f $e
close $f
exit
