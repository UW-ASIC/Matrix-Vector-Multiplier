v {xschem version=3.4.4 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 60 0 100 0 {
lab=#net1}
N 60 100 100 100 {
lab=#net1}
N 100 -0 100 100 {
lab=#net1}
N 100 100 100 520 {
lab=#net1}
N 60 700 100 700 {
lab=#net1}
N 100 520 100 700 {
lab=#net1}
N 60 600 100 600 {
lab=#net1}
N 60 500 100 500 {
lab=#net1}
N 60 400 100 400 {
lab=#net1}
N 60 300 100 300 {
lab=#net1}
N 60 200 100 200 {
lab=#net1}
N 100 350 200 350 {
lab=#net1}
N 140 460 160 460 {
lab=#net2}
N 140 430 200 430 {
lab=#net2}
N 200 410 200 430 {
lab=#net2}
N 200 430 290 430 {
lab=#net2}
N 200 490 200 510 {
lab=GND}
N 200 510 330 510 {
lab=GND}
N 330 460 330 510 {
lab=GND}
N 330 350 330 400 {
lab=Iout}
N 330 350 420 350 {
lab=Iout}
N -50 -0 0 0 {
lab=D7}
N -50 100 0 100 {
lab=D6}
N -50 200 0 200 {
lab=D5}
N -50 300 0 300 {
lab=D4}
N -50 400 0 400 {
lab=D3}
N -50 500 0 500 {
lab=D2}
N -50 600 0 600 {
lab=D1}
N -50 700 0 700 {
lab=D0}
N 140 430 140 460 {}
C {sky130_fd_pr/res_generic_l1.sym} 30 0 3 0 {name=R1
W=1
L=1
model=res_generic_l1
mult=1}
C {sky130_fd_pr/res_generic_l1.sym} 30 100 3 0 {name=R2
W=1
L=1
model=res_generic_l1
mult=1}
C {sky130_fd_pr/res_generic_l1.sym} 30 200 3 0 {name=R3
W=1
L=1
model=res_generic_l1
mult=1}
C {sky130_fd_pr/res_generic_l1.sym} 30 300 3 0 {name=R4
W=1
L=1
model=res_generic_l1
mult=1}
C {sky130_fd_pr/res_generic_l1.sym} 30 400 3 0 {name=R5
W=1
L=1
model=res_generic_l1
mult=1}
C {sky130_fd_pr/res_generic_l1.sym} 30 500 3 0 {name=R6
W=1
L=1
model=res_generic_l1
mult=1}
C {sky130_fd_pr/res_generic_l1.sym} 30 600 3 0 {name=R7
W=1
L=1
model=res_generic_l1
mult=1}
C {sky130_fd_pr/res_generic_l1.sym} 30 700 3 0 {name=R8
W=1
L=1
model=res_generic_l1
mult=1}
C {sky130_fd_pr/res_generic_l1.sym} 200 380 0 0 {name=R9
W=1
L=1
model=res_generic_l1
mult=1}
C {sky130_fd_pr/nfet3_01v8.sym} 180 460 0 0 {name=M1
L=0.15
W=1
body=GND
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
C {sky130_fd_pr/nfet3_01v8.sym} 310 430 0 0 {name=M2
L=0.15
W=1
body=GND
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
C {devices/opin.sym} 420 350 0 0 {name=p1 lab=Iout}
C {devices/ipin.sym} -50 0 0 0 {name=p2 lab=D7}
C {devices/ipin.sym} -50 100 0 0 {name=p3 lab=D6}
C {devices/ipin.sym} -50 200 0 0 {name=p4 lab=D5}
C {devices/ipin.sym} -50 300 0 0 {name=p5 lab=D4}
C {devices/ipin.sym} -50 400 0 0 {name=p6 lab=D3}
C {devices/ipin.sym} -50 500 0 0 {name=p7 lab=D2}
C {devices/ipin.sym} -50 600 0 0 {name=p8 lab=D1}
C {devices/ipin.sym} -50 700 0 0 {name=p9 lab=D0}
C {devices/gnd.sym} 260 510 0 0 {name=l1 lab=GND}
