# Magic LVS extraction batch script for Sky130
# Usage: magic -dnull -noconsole -T sky130A < extract_lvs.tcl
# Environment: GDS_FILE, CELL_NAME, OUT_SPICE

set gds_file $::env(GDS_FILE)
set cell_name $::env(CELL_NAME)
set out_spice $::env(OUT_SPICE)

gds read $gds_file
load $cell_name

# Flatten for extraction
flatten $cell_name\_flat
load $cell_name\_flat

# Extract
extract all
ext2spice lvs
ext2spice -o $out_spice
ext2spice

puts "LVS netlist written to $out_spice"
quit -noprompt
