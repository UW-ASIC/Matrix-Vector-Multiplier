v {xschem version=3.4.4 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N -150 50 -100 50 {lab=GND}
N -150 50 -150 70 {lab=GND}
N -220 -50 -100 -50 {lab=Iin}
N -160 -200 -160 -50 {lab=Iin}
N 170 0 220 0 {lab=Vout}
N 220 -200 220 0 {lab=Vout}
N 220 0 250 0 {lab=Vout}
N 60 -200 220 -200 {lab=Vout}
N -160 -200 0 -200 {lab=Iin}
N -70 -360 -70 -200 {lab=Iin}
N -70 -360 0 -360 {lab=Iin}
N 60 -360 120 -360 {lab=Vout}
N 120 -360 120 -200 {lab=Vout}
N -280 -50 -220 -50 {lab=Iin}
C {OpAmps/OpAmp_Optimized/OpAmp_OPT.sym} 50 0 0 0 {name=x1}
C {devices/gnd.sym} -150 70 0 0 {name=l1 lab=GND}
C {devices/ipin.sym} -280 -50 0 0 {name=p1 lab=Iin}
C {devices/opin.sym} 250 0 0 0 {name=p2 lab=Vout}
C {sky130_fd_pr/res_generic_m4.sym} 30 -200 3 0 {name=R1
W=1
L=1
model=res_generic_m4
mult=1
}
C {sky130_fd_pr/cap_mim_m3_1.sym} -190 -20 2 0 {name=C1
model=cap_mim_m3_1
W=1
L=1
MF=1
spiceprefix=X
}
C {devices/gnd.sym} -190 10 0 0 {name=l2 lab=GND}
C {sky130_fd_pr/cap_mim_m3_1.sym} 30 -360 1 0 {name=C2
model=cap_mim_m3_1
W=1
L=1
MF=1
spiceprefix=X
}
C {devices/iopin.sym} 30 -90 3 0 {name=p3 lab=VDD}
C {devices/iopin.sym} 30 90 1 0 {name=p4 lab=VSS}
C {devices/iopin.sym} -30 130 1 0 {name=p5 lab=Vbias}
