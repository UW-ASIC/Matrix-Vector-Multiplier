v {xschem version=3.4.4 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N -250 -50 -250 -0 {
lab=GND}
N -250 -0 -250 50 {
lab=GND}
N -190 50 -130 50 {
lab=V+}
N -190 -50 -130 -50 {
lab=V-}
C {Operational_Amplifiers/OpAmp.sym} 20 0 0 0 {name=x1}
C {devices/vsource.sym} -220 50 1 0 {name=V1 value="DC 0.9" savecurrent=false}
C {devices/code_shown.sym} 240 120 0 0 {name=s1 only_toplevel=false value="
* DC Operating Point Analysis
.op
.control
run
print all
.endc
"}
C {devices/gnd.sym} 0 90 0 0 {name=l2 lab=GND}
C {devices/lab_pin.sym} 140 0 2 0 {name=p1 sig_type=std_logic lab=out}
C {devices/lab_pin.sym} -150 50 3 0 {name=p2 sig_type=std_logic lab=V+}
C {devices/lab_pin.sym} -150 -50 3 0 {name=p3 sig_type=std_logic lab=V-}
C {devices/vsource.sym} -220 -50 1 0 {name=V3 value="DC 0.9V" savecurrent=false}
C {devices/gnd.sym} -250 0 1 0 {name=l4 lab=GND}
C {sky130_fd_pr/corner.sym} 300 -100 0 0 {name=CORNER only_toplevel=false corner=tt}
C {devices/vsource.sym} 30 -90 3 0 {name=V2 value="DC 1.8V" savecurrent=false}
C {devices/gnd.sym} 60 -90 3 0 {name=l6 lab=GND}
C {devices/lab_pin.sym} 0 -90 1 0 {name=p4 sig_type=std_logic lab=vdd}
C {devices/gnd.sym} -60 130 0 0 {name=l1 lab=GND}
