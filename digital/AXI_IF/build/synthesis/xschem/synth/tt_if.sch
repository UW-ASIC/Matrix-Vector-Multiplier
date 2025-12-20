v {xschem version=3.4.5 file_version=1.2}
G {}
K {type=subcircuit}
V {}
S {}
E {}
C {devices/ipin.sym} 0 0 0 0 {name=pi_clk lab=i_clk}
C {devices/ipin.sym} 0 40 0 0 {name=pi_ena lab=i_ena}
C {devices/ipin.sym} 0 80 0 0 {name=pi_rst_n lab=i_rst_n}
C {devices/ipin.sym} 0 120 0 0 {name=pui_in lab=ui_in}
C {devices/ipin.sym} 0 160 0 0 {name=puio_in lab=uio_in}
C {devices/opin.sym} 0 200 0 0 {name=puio_oe lab=uio_oe}
C {devices/opin.sym} 0 240 0 0 {name=puio_out lab=uio_out}
C {devices/opin.sym} 0 280 0 0 {name=puo_out lab=uo_out}

C {synth/tt_if_inner.sym} 300 100 0 0 {name=X1
spice_sym_def=".include ../../runs/tt_if_full/final/spice/tt_if.spice"}
C {devices/lab_pin.sym} 150 66 0 0 {name=li_clk lab=i_clk}
C {devices/lab_pin.sym} 150 82 0 0 {name=li_ena lab=i_ena}
C {devices/lab_pin.sym} 150 98 0 0 {name=li_rst_n lab=i_rst_n}
C {devices/lab_pin.sym} 150 114 0 0 {name=lui_in lab=ui_in}
C {devices/lab_pin.sym} 150 130 0 0 {name=luio_in lab=uio_in}
C {devices/lab_pin.sym} 390 75 0 1 {name=luio_oe lab=uio_oe}
C {devices/lab_pin.sym} 390 100 0 1 {name=luio_out lab=uio_out}
C {devices/lab_pin.sym} 390 125 0 1 {name=luo_out lab=uo_out}
