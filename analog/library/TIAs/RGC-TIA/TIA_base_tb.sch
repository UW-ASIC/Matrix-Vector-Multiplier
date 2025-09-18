v {xschem version=3.4.4 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 180 -40 180 -20 {
lab=VDD}
N 160 -20 180 -20 {
lab=VDD}
N 180 -120 180 -100 {
lab=GND}
N 160 20 180 20 {
lab=GND}
N 180 20 180 40 {
lab=GND}
N -160 -20 -160 -0 {
lab=Iin}
N -160 -20 -140 -20 {
lab=Iin}
N -160 150 -160 170 {
lab=GND}
N 160 -0 180 -0 {
lab=Vout}
N -160 60 -160 90 {
lab=#net1}
C {Transamp.sym} 10 0 0 0 {name=x1}
C {vsource.sym} 180 -70 2 0 {name=V1 value=1.8 savecurrent=false}
C {gnd.sym} 180 40 0 0 {name=l1 lab=GND}
C {gnd.sym} 180 -120 2 0 {name=l2 lab=GND}
C {sky130_fd_pr/corner.sym} 240 -140 0 0 {name=CORNER only_toplevel=false corner=tt}
C {code_shown.sym} 250 50 0 0 {name=SPICE only_toplevel=false value=".tran 0.1n 10u
.save all"}
C {isource.sym} -160 120 2 0 {name=I0 value="0"}
C {gnd.sym} -160 170 0 0 {name=l3 lab=GND}
C {lab_pin.sym} 180 -20 2 0 {name=p1 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 180 0 2 0 {name=p2 sig_type=std_logic lab=Vout}
C {lab_pin.sym} -160 -20 0 0 {name=p3 sig_type=std_logic lab=Iin}
C {vsource.sym} -160 30 2 0 {name=Vmeas value=0 savecurrent=true}
