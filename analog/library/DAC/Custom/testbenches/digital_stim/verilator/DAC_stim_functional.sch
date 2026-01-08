v {xschem version=3.4.5 file_version=1.2}
G {}
K {type=subcircuit}
V {}
S {}
E {}
C {devices/opin.sym} 0 0 0 0 {name=pdac_out lab=dac_out}
C {devices/opin.sym} 0 40 0 0 {name=pdac_out_n lab=dac_out_n}

C {testbenches/digital_stim/verilator/DAC_stim_functional_inner.sym} 300 100 0 0 {name=DAC_stim model=DAC_stim
device_model=".model DAC_stim d_cosim simulation=\"../DAC_stim.so\""
tclcommand="edit_file [abs_sym_path ../DAC_stim.v]"}
C {devices/lab_pin.sym} 390 83 0 1 {name=ldac_out lab=dac_out}
C {devices/lab_pin.sym} 390 116 0 1 {name=ldac_out_n lab=dac_out_n}
