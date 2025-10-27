v {xschem version=3.4.4 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N -50 0 0 0 {
lab=#net1}
N -50 100 -0 100 {
lab=I-S_out}
N -90 30 -90 70 {
lab=#net1}
N -90 30 -50 30 {
lab=#net1}
N -50 0 -50 30 {
lab=#net1}
N -90 130 -50 130 {
lab=I-S_out}
N -50 100 -50 130 {
lab=I-S_out}
N -90 -30 40 -30 {
lab=V_in}
N 40 30 40 70 {
lab=#net2}
N -90 -60 -90 -30 {
lab=V_in}
N 180 30 180 70 {
lab=#net3}
N -20 0 -20 40 {
lab=#net1}
N -20 40 140 40 {
lab=#net1}
N 140 -0 140 40 {
lab=#net1}
N -20 60 140 60 {
lab=I-S_out}
N -20 60 -20 100 {
lab=I-S_out}
N 140 60 140 100 {
lab=I-S_out}
N 320 30 320 70 {
lab=#net4}
N 280 0 280 40 {
lab=#net1}
N 280 60 280 100 {
lab=I-S_out}
N 460 30 460 70 {
lab=#net5}
N 420 0 420 40 {
lab=#net1}
N 420 60 420 100 {
lab=I-S_out}
N 140 40 280 40 {
lab=#net1}
N 280 40 420 40 {
lab=#net1}
N 280 60 420 60 {
lab=I-S_out}
N 140 60 280 60 {
lab=I-S_out}
N 40 -30 180 -30 {
lab=V_in}
N 180 -30 320 -30 {
lab=V_in}
N 320 -30 460 -30 {
lab=V_in}
N -90 130 -90 170 {
lab=I-S_out}
N 40 130 40 160 {
lab=#net6}
N 10 160 40 160 {
lab=#net6}
N 180 130 180 160 {
lab=#net7}
N 150 160 180 160 {
lab=#net7}
N 320 130 320 160 {
lab=#net8}
N 290 160 320 160 {
lab=#net8}
N 460 130 460 160 {
lab=#net9}
N 430 160 460 160 {
lab=#net9}
N 40 240 460 240 {
lab=#net10}
N 10 260 430 260 {
lab=#net11}
N 40 220 40 240 {
lab=#net10}
N 180 220 180 240 {
lab=#net10}
N 320 220 320 240 {
lab=#net10}
N 460 220 460 240 {
lab=#net10}
N 430 220 430 260 {
lab=#net11}
N 290 220 290 260 {
lab=#net11}
N 150 220 150 260 {
lab=#net11}
N 10 220 10 260 {
lab=#net11}
N 40 130 40 160 {
lab=#net6}
N 10 160 40 160 {
lab=#net6}
N 530 260 530 270 {
lab=#net11}
N 530 330 530 350 {
lab=GND}
N 560 330 560 350 {
lab=GND}
N 530 350 560 350 {
lab=GND}
N 560 350 560 370 {
lab=GND}
N 460 240 560 240 {
lab=#net10}
N 560 240 560 270 {
lab=#net10}
N 430 260 530 260 {
lab=#net11}
N -30 190 -30 280 {
lab=B1}
N 110 190 110 280 {
lab=B2}
N 250 190 250 280 {
lab=B3}
N 390 190 390 280 {
lab=B1}
N 80 190 80 300 {
lab=B1_bar}
N 220 190 220 300 {
lab=B2_bar}
N 360 190 360 300 {
lab=B3_bar}
N 500 190 500 300 {
lab=B4_bar}
C {sky130_fd_pr/pfet_01v8.sym} 20 0 0 0 {name=M1
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
C {sky130_fd_pr/pfet_01v8.sym} 20 100 0 0 {name=M2
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
C {sky130_fd_pr/pfet_01v8.sym} -70 0 0 1 {name=M3
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
C {sky130_fd_pr/pfet_01v8.sym} -70 100 0 1 {name=M4
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
C {ipin.sym} -90 -60 0 0 {name=p1 lab=V_in}
C {opin.sym} -90 170 2 0 {name=p2 lab=I-S_out}
C {sky130_fd_pr/pfet_01v8.sym} 160 0 0 0 {name=M5
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
C {sky130_fd_pr/pfet_01v8.sym} 160 100 0 0 {name=M6
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
C {sky130_fd_pr/pfet_01v8.sym} 300 0 0 0 {name=M7
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
C {sky130_fd_pr/pfet_01v8.sym} 300 100 0 0 {name=M8
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
C {sky130_fd_pr/pfet_01v8.sym} 440 0 0 0 {name=M9
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
C {sky130_fd_pr/pfet_01v8.sym} 440 100 0 0 {name=M10
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
C {sky130_fd_pr/pfet_01v8.sym} 20 100 0 0 {name=M11
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
C {sky130_fd_pr/pfet_01v8.sym} -10 190 0 0 {name=M12
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
C {sky130_fd_pr/pfet_01v8.sym} 60 190 0 1 {name=M13
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
C {sky130_fd_pr/pfet_01v8.sym} 130 190 0 0 {name=M14
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
C {sky130_fd_pr/pfet_01v8.sym} 200 190 0 1 {name=M15
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
C {sky130_fd_pr/pfet_01v8.sym} 270 190 0 0 {name=M16
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
C {sky130_fd_pr/pfet_01v8.sym} 340 190 0 1 {name=M17
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
C {sky130_fd_pr/pfet_01v8.sym} 410 190 0 0 {name=M18
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
C {sky130_fd_pr/pfet_01v8.sym} 480 190 0 1 {name=M19
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
C {sky130_fd_pr/res_generic_l1.sym} 560 300 0 0 {name=R1
W=1
L=1
model=res_generic_l1
mult=1}
C {sky130_fd_pr/pfet_01v8.sym} -10 190 0 0 {name=M20
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
C {sky130_fd_pr/pfet_01v8.sym} 60 190 0 1 {name=M21
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
C {sky130_fd_pr/res_generic_l1.sym} 530 300 0 0 {name=R2
W=1
L=1
model=res_generic_l1
mult=1}
C {gnd.sym} 560 370 0 0 {name=l1 lab=GND}
C {ipin.sym} -30 280 2 0 {name=p3 lab=B1}
C {ipin.sym} -90 -60 0 0 {name=p4 lab=V_in}
C {ipin.sym} 80 300 0 0 {name=p5 lab=B1_bar}
C {ipin.sym} 110 280 2 0 {name=p6 lab=B2}
C {ipin.sym} 250 280 2 0 {name=p7 lab=B3}
C {ipin.sym} 390 280 2 0 {name=p8 lab=B4}
C {ipin.sym} 220 300 0 0 {name=p9 lab=B2_bar}
C {ipin.sym} 360 300 0 0 {name=p10 lab=B3_bar}
C {ipin.sym} 500 300 0 0 {name=p11 lab=B4_bar}
