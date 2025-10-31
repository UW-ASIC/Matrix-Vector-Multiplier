v {xschem version=3.4.4 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N -40 0 -40 50 {
lab=Iin}
N -40 0 40 0 {
lab=Iin}
N -40 -40 -40 0 {
lab=Iin}
N 80 -70 80 -30 {
lab=Iout}
N 80 0 100 0 {
lab=GND}
N -70 80 -60 80 {
lab=GND}
N -70 80 -70 110 {
lab=GND}
N -70 110 -40 110 {
lab=GND}
C {sky130_fd_pr/nfet_01v8_lvt.sym} 60 0 0 0 {name=M1
L=0.15
W=1
nf=1
mult=1
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=nfet_01v8_lvt
spiceprefix=X
}
C {devices/ipin.sym} -40 -40 1 0 {name=p1 lab=Iin}
C {devices/opin.sym} 80 -70 3 0 {name=p2 lab=Iout
}
C {devices/gnd.sym} 100 0 0 0 {name=l2 lab=GND}
C {devices/gnd.sym} -40 110 0 0 {name=l1 lab=GND}
C {devices/gnd.sym} 80 30 0 0 {name=l3 lab=VSS}
C {sky130_fd_pr/res_high_po_5p73.sym} -40 80 0 0 {name=R1
W=5.73
L=11
model=res_high_po_5p73
spiceprefix=X
mult=1}
