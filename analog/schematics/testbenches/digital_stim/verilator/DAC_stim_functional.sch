v {xschem version=3.4.5 file_version=1.2}
G {}
K {type=subcircuit}
V {}
S {}
E {}
C {devices/ipin.sym} 0 0 0 0 {name=pclk lab=clk}
C {devices/ipin.sym} 0 40 0 0 {name=prst_n lab=rst_n}
C {devices/opin.sym} 0 80 0 0 {name=pdac_out lab=dac_out}

C {verilator/DAC_stim_functional_inner.sym} 300 100 0 0 {name=DAC_stim model=DAC_stim
device_model=".model DAC_stim d_cosim simulation=\"./DAC_stim.so\""
tclcommand="edit_file [abs_sym_path ../../rtl/DAC_stim.sv]"}
C {devices/lab_pin.sym} 150 83 0 0 {name=lclk lab=clk}
C {devices/lab_pin.sym} 150 116 0 0 {name=lrst_n lab=rst_n}
C {devices/lab_pin.sym} 390 100 0 1 {name=ldac_out lab=dac_out}
