v {xschem version=3.4.4 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N -100 160 -100 200 {
lab=#net1}
N -100 200 0 200 {
lab=#net1}
N 0 200 100 200 {
lab=#net1}
N 100 160 100 200 {
lab=#net1}
N -100 80 -100 100 {
lab=#net2}
N 100 80 100 100 {
lab=#net3}
N -20 30 20 -10 {
lab=VoutX}
N 100 -10 100 0 {
lab=VoutX}
N -20 -10 20 30 {
lab=VoutX}
N -100 -10 -100 0 {
lab=VoutX}
N -100 -90 -100 -10 {
lab=VoutX}
N 100 -90 100 -10 {
lab=VoutX}
N -20 -130 20 -90 {
lab=VoutX}
N -20 -90 20 -130 {
lab=VoutX}
N -100 -220 -100 -160 {
lab=VDD}
N -100 -220 100 -220 {
lab=VDD}
N 100 -220 100 -160 {
lab=VDD}
N 0 200 0 240 {
lab=#net1}
N 0 300 0 340 {
lab=GND}
N 100 -90 270 -90 {
lab=VoutX}
N 270 -100 270 -90 {
lab=VoutX}
N -270 -100 -270 -90 {
lab=VoutX}
N -270 -90 -100 -90 {
lab=VoutX}
N 400 -100 400 80 {
lab=#net3}
N 100 80 400 80 {
lab=#net3}
N -400 80 -100 80 {
lab=#net2}
N -400 -100 -400 80 {
lab=#net2}
N -320 -130 -310 -130 {
lab=CLK}
N -320 -130 -320 -40 {
lab=CLK}
N -460 -40 -320 -40 {
lab=CLK}
N -460 -130 -460 -40 {
lab=CLK}
N -460 -130 -440 -130 {
lab=CLK}
N 320 -40 460 -40 {
lab=CLK}
N 460 -130 460 -40 {
lab=CLK}
N 440 -130 460 -130 {
lab=CLK}
N 310 -130 320 -130 {
lab=CLK}
N 320 -130 320 -40 {
lab=CLK}
N -400 -220 -400 -160 {
lab=VDD}
N -270 -220 -100 -220 {
lab=VDD}
N -270 -220 -270 -160 {
lab=VDD}
N 270 -220 400 -220 {
lab=VDD}
N 400 -220 400 -160 {
lab=VDD}
N 270 -220 270 -160 {
lab=VDD}
N -460 270 -40 270 {
lab=CLK}
N -460 -40 -460 270 {
lab=CLK}
N -460 340 0 340 {
lab=GND}
N 100 -100 100 -90 {
lab=VoutX}
N -100 -100 -100 -90 {
lab=VoutX}
N 100 60 100 80 {
lab=#net3}
N -100 60 -100 80 {
lab=#net2}
N -320 -40 320 -40 {
lab=CLK}
N -400 -220 -270 -220 {
lab=VDD}
N 100 -220 270 -220 {
lab=VDD}
N -460 -220 -400 -220 {
lab=VDD}
N 140 130 140 230 {
lab=Vin2}
N -340 130 -140 130 {
lab=Vin1}
N -340 230 140 230 {
lab=Vin2}
N -60 30 -20 30 {}
N 20 30 60 30 {}
N 20 -10 100 -10 {}
N -100 -10 -20 -10 {}
N -100 -90 -20 -90 {}
N -60 -130 -20 -130 {}
N 20 -130 60 -130 {}
N 20 -90 100 -90 {}
C {sky130_fd_pr/nfet3_01v8.sym} -120 130 0 0 {name=M1
L=0.15
W=1
body=GND
nf=1 mult=1
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet3_01v8.sym} 120 130 0 1 {name=M2
L=0.15
W=1
body=GND
nf=1 mult=1
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet3_01v8.sym} -80 30 0 1 {name=M3
L=0.15
W=1
body=GND
nf=1 mult=1
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet3_01v8.sym} 80 30 0 0 {name=M4
L=0.15
W=1
body=GND
nf=1 mult=1
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet3_01v8.sym} 80 -130 0 0 {name=M6
L=0.15
W=2
body=VDD
nf=1 mult=1
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet3_01v8.sym} -80 -130 0 1 {name=M5
L=0.15
W=2
body=VDD
nf=1 mult=1
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet3_01v8.sym} -20 270 0 0 {name=M7
L=0.15
W=1
body=GND
nf=1 mult=1
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet3_01v8.sym} -420 -130 0 0 {name=M8
L=0.15
W=2
body=VDD
nf=1 mult=1
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet3_01v8.sym} 420 -130 0 1 {name=M9
L=0.15
W=2
body=VDD
nf=1 mult=1
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet3_01v8.sym} -80 -130 0 1 {name=M10
L=0.15
W=2
body=VDD
nf=1 mult=1
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet3_01v8.sym} -290 -130 0 0 {name=M11
L=0.15
W=2
body=VDD
nf=1 mult=1
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet3_01v8.sym} 290 -130 0 1 {name=M12
L=0.15
W=2
body=VDD
nf=1 mult=1
model=pfet_01v8
spiceprefix=X
}
C {ipin.sym} -460 340 0 0 {name=p2 lab=GND}
C {gnd.sym} 0 340 0 0 {name=l1 lab=GND}
C {opin.sym} -100 -60 0 0 {name=p3 lab=VoutX}
C {vdd.sym} -400 -220 0 0 {name=l2 lab=VDD}
C {ipin.sym} -460 -220 0 0 {name=p1 lab=VDD}
C {ipin.sym} -460 -40 0 0 {name=p4 lab=CLK}
C {ipin.sym} -340 130 0 0 {name=p5 lab=Vin1}
C {ipin.sym} -340 230 0 0 {name=p6 lab=Vin2}
C {opin.sym} 100 -60 0 0 {name=p7 lab=VoutY}
