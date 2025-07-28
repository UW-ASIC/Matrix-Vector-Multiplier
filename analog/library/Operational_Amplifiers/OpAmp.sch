v {xschem version=3.4.4 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
T {Different Input Stage} -300 -240 0 0 0.4 0.4 {}
T {Differential Output} 40 -60 0 0 0.1 0.1 {}
T {Amplifier Stage} 190 -230 0 0 0.4 0.4 {}
T {https://aicdesign.org/wp-content/uploads/2018/08/lecture23-160311.pdf} -390 -350 0 0 0.4 0.4 {}
N -320 30 -320 60 {
lab=#net1}
N -320 60 -60 60 {
lab=#net1}
N -60 30 -60 60 {
lab=#net1}
N -200 60 -200 90 {
lab=#net1}
N -320 -80 -320 -30 {
lab=#net2}
N -320 -170 -320 -140 {
lab=VDD}
N -320 -170 -70 -170 {
lab=VDD}
N -360 -60 -320 -60 {
lab=#net2}
N -360 -110 -360 -60 {
lab=#net2}
N -320 -60 -230 -60 {
lab=#net2}
N -230 -60 -110 -60 {
lab=#net2}
N -110 -110 -110 -60 {
lab=#net2}
N -60 -80 -60 -30 {
lab=xxx}
N -60 -170 -60 -140 {
lab=VDD}
N -70 -170 -60 -170 {
lab=VDD}
N -110 -110 -100 -110 {
lab=#net2}
N -320 180 -200 180 {
lab=VSS}
N -200 150 -200 180 {
lab=VSS}
N -380 -170 -320 -170 {
lab=VDD}
N -380 180 -320 180 {
lab=VSS}
N -200 180 90 180 {
lab=VSS}
N -60 -170 90 -170 {
lab=VDD}
N 90 -170 170 -170 {
lab=VDD}
N 90 180 170 180 {
lab=VSS}
N -60 -50 170 -50 {
lab=xxx}
N 280 120 330 120 {
lab=Vbias}
N 170 -50 210 -50 {
lab=xxx}
N 170 -110 170 -50 {
lab=xxx}
N 170 -110 330 -110 {
lab=xxx}
N 370 -170 370 -140 {
lab=VDD}
N 170 -170 370 -170 {
lab=VDD}
N 350 -50 370 -50 {
lab=Vout}
N 370 -80 370 -50 {
lab=Vout}
N 370 -50 370 90 {
lab=Vout}
N 170 180 370 180 {
lab=VSS}
N 370 150 370 180 {
lab=VSS}
N 370 -50 430 -50 {
lab=Vout}
N 210 -50 230 -50 {
lab=xxx}
N 290 -50 350 -50 {
lab=Vout}
C {sky130_fd_pr/nfet_01v8.sym} -340 0 0 0 {name=M1
L=0.15
W=10
nf=1 
mult=1
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} -80 0 0 0 {name=M2
L=0.15
W=10
nf=1 
mult=1
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} -220 120 0 0 {name=M3
L=0.3
W=15
nf=1 
mult=1
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet_01v8.sym} -340 -110 0 0 {name=M4
L=0.15
W=5
nf=1
mult=1
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet_01v8.sym} -80 -110 0 0 {name=M5
L=0.15
W=5
nf=1
mult=1
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
C {devices/ipin.sym} -240 120 0 0 {name=p1 lab=Vbias}
C {devices/ipin.sym} -100 0 0 0 {name=p7 lab=Vplus}
C {devices/ipin.sym} -360 0 0 0 {name=p4 lab=Vminus}
C {sky130_fd_pr/pfet_01v8.sym} 350 -110 0 0 {name=M6
L=0.15
W=20
nf=1
mult=1
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 350 120 0 0 {name=M7
L=0.15
W=10
nf=1 
mult=1
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {devices/opin.sym} 430 -50 0 0 {name=p6 lab=Vout}
C {devices/iopin.sym} -380 -170 2 0 {name=p2 lab=VDD}
C {devices/iopin.sym} -380 180 2 0 {name=p3 lab=VSS}
C {devices/lab_pin.sym} -240 120 3 0 {name=p5 sig_type=std_logic lab=Vbias}
C {devices/lab_pin.sym} 280 120 0 0 {name=p16 sig_type=std_logic lab=Vbias}
C {sky130_fd_pr/cap_mim_m3_2.sym} 260 -50 1 0 {name=C2 model=cap_mim_m3_2 W=12 L=1 MF=12 spiceprefix=X}
C {devices/gnd.sym} -360 180 0 0 {name=l1 lab=VSS}
C {devices/vdd.sym} -360 -170 0 0 {name=l2 lab=VDD}
C {devices/vdd.sym} -320 -110 1 0 {name=l3 lab=VDD}
C {devices/vdd.sym} -60 -110 1 0 {name=l4 lab=VDD}
C {devices/gnd.sym} -60 0 3 0 {name=l5 lab=VSS}
C {devices/gnd.sym} -320 0 3 0 {name=l6 lab=VSS}
C {devices/gnd.sym} 370 120 3 0 {name=l7 lab=VSS}
C {devices/vdd.sym} 370 -110 1 0 {name=l8 lab=VDD}
C {devices/gnd.sym} -200 120 3 0 {name=l9 lab=VSS}
C {devices/lab_pin.sym} 100 -50 1 0 {name=p8 sig_type=std_logic lab=V1st}
