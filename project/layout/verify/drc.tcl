# Magic DRC batch script for Sky130
# Usage: magic -dnull -noconsole -T sky130A < drc.tcl
# Environment: GDS_FILE, CELL_NAME, REPORT_FILE

set gds_file $::env(GDS_FILE)
set cell_name $::env(CELL_NAME)
set report_file $::env(REPORT_FILE)

gds read $gds_file
load $cell_name

# Run DRC
select top cell
drc catchup
drc count

# Write report
set fh [open $report_file w]
puts $fh "DRC Report: $cell_name"
puts $fh "GDS: $gds_file"
puts $fh "---"
set count [drc listall count]
puts $fh "Total violations: $count"
puts $fh ""
set errors [drc listall why]
foreach {msg} $errors {
    puts $fh $msg
}
close $fh

puts "DRC: $count violations written to $report_file"
quit -noprompt
