v {xschem version=3.4.8RC file_version=1.2}
G {}
K {}
V {}
S {}
F {}
E {}
N -10 -40 -10 -30 {lab=VS}
N -10 -40 150 -40 {lab=VS}
N 150 -40 150 -30 {lab=VS}
N -10 30 -10 40 {lab=VD}
N -10 40 150 40 {lab=VD}
N 150 30 150 40 {lab=VD}
N 70 40 70 70 {lab=VD}
N 70 -80 70 -40 {lab=VS}
C {sky130_fd_pr/nfet_01v8.sym} 170 0 2 0 {name=M1
W=1
L=0.15
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
C {sky130_fd_pr/pfet_01v8.sym} -30 0 0 0 {name=M2
W=1
L=0.15
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
C {ipin.sym} -50 0 0 0 {name=p1 lab=VPG}
C {ipin.sym} -10 0 2 0 {name=p2 lab=VPB}
C {ipin.sym} 150 0 0 0 {name=p3 lab=VNB}
C {ipin.sym} 190 0 2 0 {name=p4 lab=VNG}
C {ipin.sym} 70 -80 1 0 {name=p5 lab=VS}
C {opin.sym} 70 70 1 0 {name=p6 lab=VD}
