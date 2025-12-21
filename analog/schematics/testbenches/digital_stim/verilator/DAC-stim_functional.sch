v {xschem version=3.4.7 file_version=1.2}
G {}
K {type=subcircuit}
V {}
S {}
E {}
C {devices/ipin.sym} 0 0 0 0 {name=plogic lab=logic}
C {devices/ipin.sym} 0 40 0 0 {name=plogic lab=logic}
C {devices/opin.sym} 0 80 0 0 {name=plogic lab=logic}
C {testbenches/digital_stim/verilator/DAC-stim_functional_inner.sym} 300 100 0 0 {name=DAC_stim model=DAC_stim
device_model=".model DAC_stim d_cosim simulation="./DAC_stim.so""
tclcommand="edit_file [abs_sym_path ../../DAC-stim.v]"}
C {devices/lab_pin.sym} 150 83 0 0 {name=llogic lab=logic}
C {devices/lab_pin.sym} 150 116 0 0 {name=llogic lab=logic}
C {devices/lab_pin.sym} 390 100 0 1 {name=llogic lab=logic}
