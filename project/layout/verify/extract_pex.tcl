# Magic parasitic extraction batch script for Sky130
# Usage: magic -dnull -noconsole -T sky130A < extract_pex.tcl
# Environment: GDS_FILE, CELL_NAME, OUT_SPICE

set gds_file $::env(GDS_FILE)
set cell_name $::env(CELL_NAME)
set out_spice $::env(OUT_SPICE)

gds read $gds_file
load $cell_name

# Flatten for extraction
flatten $cell_name\_flat
load $cell_name\_flat

# Full parasitic extraction
extract all
extract do resistance
extract do capacitance
extract do coupling

# Set thresholds — capture all significant parasitics
ext2spice lvs
ext2spice cthresh 0.01
ext2spice rthresh 100
ext2spice extresist on
ext2spice -o $out_spice
ext2spice

puts "PEX netlist written to $out_spice"
quit -noprompt
