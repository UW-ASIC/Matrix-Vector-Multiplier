v {xschem version=3.4.4 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 90 -20 120 -20 {
lab=Vout}
N -120 -20 -90 -20 {
lab=Iin}
C {TIA/template/TIA.sym} 0 0 0 0 {name=x1}
C {devices/isource.sym} -150 -20 3 0 {name=I0 value=1m}
C {devices/vsource.sym} 0 -110 2 0 {name=V1 value=3 savecurrent=false}
C {devices/vsource.sym} -10 110 0 0 {name=V2 value=3 savecurrent=false}
C {devices/gnd.sym} 10 80 0 0 {name=l1 lab=GND}
C {devices/gnd.sym} -10 140 0 0 {name=l2 lab=GND}
C {devices/gnd.sym} 0 -140 2 0 {name=l3 lab=GND}
C {devices/lab_pin.sym} 120 -20 2 0 {name=p1 sig_type=std_logic lab=Vout}
C {devices/lab_pin.sym} -110 -20 1 0 {name=p2 sig_type=std_logic lab=Iin}
C {devices/code_shown.sym} 220 110 0 0 {name=s1 only_toplevel=false value=blabla}
C {sky130_fd_pr/corner.sym} 270 -80 0 0 {name=CORNER only_toplevel=false corner=tt}
