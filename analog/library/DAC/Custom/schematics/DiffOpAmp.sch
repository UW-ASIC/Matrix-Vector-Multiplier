v {xschem version=3.4.4 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 0 30 0 140 {
lab=VSS}
N 160 30 160 140 {
lab=VSS}
N 0 140 160 140 {
lab=VSS}
N 100 0 120 -0 {
lab=#net1}
N 100 -40 100 0 {
lab=#net1}
N 100 -40 160 -40 {
lab=#net1}
N 160 -40 160 -30 {
lab=#net1}
N 380 60 420 60 {
lab=Vbiasn}
N 160 140 300 140 {
lab=VSS}
N 300 140 460 140 {
lab=VSS}
N 460 90 460 140 {
lab=VSS}
N 300 90 300 140 {
lab=VSS}
N 300 0 300 30 {
lab=#net2}
N 300 0 460 0 {
lab=#net2}
N 460 0 460 30 {
lab=#net2}
N 300 -20 300 0 {
lab=#net2}
N 460 -20 460 -0 {
lab=#net2}
N 660 0 720 0 {
lab=#net3}
N 660 -40 660 0 {
lab=#net3}
N 600 -40 600 -30 {
lab=#net3}
N 600 -40 660 -40 {
lab=#net3}
N 600 30 600 140 {
lab=VSS}
N 600 140 760 140 {
lab=VSS}
N 760 30 760 140 {
lab=VSS}
N 460 140 600 140 {
lab=VSS}
N 0 -170 0 -30 {
lab=Vout_minus}
N 300 -120 300 -80 {
lab=#net4}
N 300 -320 300 -270 {
lab=VDD}
N 300 -320 460 -320 {
lab=VDD}
N 460 -320 460 -270 {
lab=VDD}
N 600 -320 760 -320 {
lab=VDD}
N 760 -320 760 -230 {
lab=VDD}
N 160 -320 300 -320 {
lab=VDD}
N 0 -320 0 -230 {
lab=VDD}
N 40 -200 300 -200 {
lab=#net4}
N 460 -160 460 -80 {
lab=#net5}
N 460 -200 720 -200 {
lab=#net5}
N 760 -170 760 -30 {
lab=Vout_plus}
N 600 -110 600 -40 {
lab=#net3}
N 160 -110 160 -40 {
lab=#net1}
N 460 -240 540 -240 {
lab=VDD}
N 160 -320 160 -170 {
lab=VDD}
N 600 -320 600 -170 {
lab=VDD}
N 200 -160 200 -140 {
lab=#net5}
N 200 -160 460 -160 {
lab=#net5}
N 560 -140 560 -120 {
lab=#net4}
N 300 -120 560 -120 {
lab=#net4}
N 600 -140 680 -140 {
lab=VDD}
N 760 -200 840 -200 {
lab=VDD}
N -80 -200 0 -200 {
lab=VDD}
N 80 -140 160 -140 {
lab=VDD}
N 220 -240 300 -240 {
lab=VDD}
N 380 -240 420 -240 {
lab=Vbiasp}
N 380 -240 380 -200 {
lab=Vbiasp}
N 380 60 380 100 {
lab=Vbiasn}
N 40 -0 100 0 {
lab=#net1}
N 640 0 660 0 {
lab=#net3}
N 300 -210 300 -200 {
lab=#net4}
N 460 -210 460 -200 {
lab=#net5}
N 0 -320 160 -320 {
lab=VDD}
N 460 -320 600 -320 {
lab=VDD}
N 460 -200 460 -160 {
lab=#net5}
N 300 -200 300 -120 {
lab=#net4}
N 340 -240 380 -240 {
lab=Vbiasp}
N 340 60 380 60 {
lab=Vbiasn}
C {sky130_fd_pr/nfet3_01v8.sym} 20 0 0 1 {name=M1
W=10
L=1
body=VSS
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
C {sky130_fd_pr/nfet3_01v8.sym} 140 0 0 0 {name=M2
W=10
L=1
body=VSS
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
C {sky130_fd_pr/nfet3_01v8.sym} 320 60 0 1 {name=M3
W=10
L=1
body=VSS
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
C {sky130_fd_pr/nfet3_01v8.sym} 440 60 0 0 {name=M4
W=10
L=1
body=VSS
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
C {sky130_fd_pr/nfet3_01v8.sym} 280 -50 0 0 {name=M5
W=10
L=1
body=VSS
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
C {sky130_fd_pr/nfet3_01v8.sym} 480 -50 0 1 {name=M6
W=10
L=1
body=VSS
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
C {sky130_fd_pr/nfet3_01v8.sym} 620 0 0 1 {name=M7
W=10
L=1
body=VSS
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
C {sky130_fd_pr/nfet3_01v8.sym} 740 0 0 0 {name=M8
W=10
L=1
body=VSS
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
C {sky130_fd_pr/pfet_01v8.sym} 440 -240 0 0 {name=M9
W=20
L=1
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
C {sky130_fd_pr/pfet_01v8.sym} 320 -240 0 1 {name=M10
W=20
L=1
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
C {sky130_fd_pr/pfet_01v8.sym} 580 -140 0 0 {name=M11
W=20
L=1
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
C {sky130_fd_pr/pfet_01v8.sym} 740 -200 0 0 {name=M12
W=20
L=1
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
C {sky130_fd_pr/pfet_01v8.sym} 180 -140 0 1 {name=M13
W=20
L=1
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
C {sky130_fd_pr/pfet_01v8.sym} 20 -200 0 1 {name=M14
W=20
L=1
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
C {devices/gnd.sym} 0 140 0 0 {name=l1 lab=VSS}
C {devices/vdd.sym} 0 -320 0 0 {name=l2 lab=VDD}
C {devices/vdd.sym} 220 -240 0 0 {name=l3 lab=VDD}
C {devices/vdd.sym} 540 -240 0 0 {name=l4 lab=VDD}
C {devices/vdd.sym} 840 -200 0 0 {name=l5 lab=VDD}
C {devices/vdd.sym} -80 -200 0 0 {name=l6 lab=VDD}
C {devices/vdd.sym} 80 -140 0 0 {name=l7 lab=VDD}
C {devices/vdd.sym} 680 -140 0 0 {name=l8 lab=VDD}
C {devices/ipin.sym} 380 100 0 0 {name=p1 lab=Vbiasn}
C {devices/ipin.sym} 380 -200 0 0 {name=p2 lab=Vbiasp
}
C {devices/ipin.sym} 260 -50 0 0 {name=p3 lab=Vminus}
C {devices/ipin.sym} 500 -50 2 0 {name=p4 lab=Vplus}
C {devices/opin.sym} 0 -140 2 0 {name=p5 lab=Vout_minus}
C {devices/opin.sym} 760 -140 0 0 {name=p6 lab=Vout_plus}
C {devices/ipin.sym} 0 -320 0 0 {name=p7 lab=VDD}
C {devices/ipin.sym} 0 140 0 0 {name=p8 lab=VSS}
