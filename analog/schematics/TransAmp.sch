v {xschem version=3.4.4 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 0 20 0 40 {
lab=#net1}
N -60 70 -40 70 {
lab=#net2}
N -0 70 0 100 {
lab=GND}
C {vsource.sym} 0 -10 2 0 {name=V1 value=3 savecurrent=false}
C {vsource.sym} -90 70 1 0 {name=V2 value=3 savecurrent=false}
C {code_shown.sym} 140 30 0 0 {name=s1 only_toplevel=false value="""
.control

save all @m.xm1.msky130_fd_pr__nfet_g5v0d10v5[gm]
save all @m.xm1.msky130_fd_pr__nfet_g5v0d10v5[id]
save all @m.xm1.msky130_fd_pr__nfet_g5v0d10v5[gds]

dc V2 0 1.8 0.01

plot @m.xm1.msky130_fd_pr__nfet_g5v0d10v5[id]*1e6
plot @m.xm1.msky130_fd_pr__nfet_g5v0d10v5[gm]*1e6
plot @m.xm1.msky130_fd_pr__nfet_g5v0d10v5[gm]/@m.xm1.msky130_fd_pr__nfet_g5v0d10v5[id] ylimit 0 35
plot @m.xm1.msky130_fd_pr__nfet_g5v0d10v5[gm]/@m.xm1.msky130_fd_pr__nfet_g5v0d10v5[gds] ylimit 0 100

.endc
.end
"""}
C {sky130_fd_pr/corner.sym} 180 -120 0 0 {name=CORNER only_toplevel=false corner=tt}
C {sky130_fd_pr/nfet_g5v0d10v5.sym} -20 70 0 0 {name=M1
W=1
L=0.5
nf=1
mult=1
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=nfet_g5v0d10v5
spiceprefix=X
}
C {gnd.sym} 0 100 0 0 {name=l1 lab=GND}
C {gnd.sym} -120 70 0 0 {name=l2 lab=GND}
C {gnd.sym} 0 -40 3 0 {name=l3 lab=GND}
