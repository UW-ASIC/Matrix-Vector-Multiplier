v {xschem version=3.4.4 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N -340 20 -160 20 {
lab=Io1}
N 360 20 360 60 {
lab=Iout}
N 150 20 360 20 {
lab=Iout}
N 150 20 150 60 {
lab=Iout}
N 250 -60 330 -60 {
lab=Iout}
N -210 -160 210 -160 {
lab=Io1}
N -250 -130 -250 -80 {
lab=Io1}
N -250 -80 -180 -80 {
lab=Io1}
N -180 -160 -180 -80 {
lab=Io1}
N -250 -80 -250 20 {
lab=Io1}
N -250 -210 -250 -190 {
lab=VDD}
N 250 -130 250 20 {
lab=Iout}
N 250 -200 250 -190 {
lab=VDD}
N 250 -160 260 -160 {
lab=VDD}
N 260 -200 260 -160 {
lab=VDD}
N 250 -200 260 -200 {
lab=VDD}
N -260 -160 -250 -160 {
lab=VDD}
N -260 -190 -260 -160 {
lab=VDD}
N -260 -200 -250 -200 {
lab=VDD}
N -260 -200 -260 -190 {
lab=VDD}
N 250 -210 250 -200 {
lab=VDD}
N -270 280 -230 280 {
lab=I1}
N -310 230 -310 250 {
lab=I1}
N -310 230 -250 230 {
lab=I1}
N -250 230 -250 280 {
lab=I1}
N -310 190 -310 230 {
lab=I1}
N -190 190 -190 250 {
lab=#net1}
N -310 310 -310 340 {
lab=GND}
N -310 340 -250 340 {
lab=GND}
N -250 340 -190 340 {
lab=GND}
N -190 310 -190 340 {
lab=GND}
N -320 280 -310 280 {
lab=GND}
N -320 280 -320 320 {
lab=GND}
N -320 320 -310 320 {
lab=GND}
N -190 280 -180 280 {
lab=GND}
N -180 280 -180 320 {
lab=GND}
N -190 320 -180 320 {
lab=GND}
N 240 290 280 290 {
lab=I2}
N 200 240 200 260 {
lab=I2}
N 200 240 260 240 {
lab=I2}
N 260 240 260 290 {
lab=I2}
N 200 200 200 240 {
lab=I2}
N 320 200 320 260 {
lab=#net2}
N 200 320 200 350 {
lab=GND}
N 200 350 260 350 {
lab=GND}
N 260 350 320 350 {
lab=GND}
N 320 320 320 350 {
lab=GND}
N 190 290 200 290 {
lab=GND}
N 190 290 190 330 {
lab=GND}
N 190 330 200 330 {
lab=GND}
N 320 290 330 290 {
lab=GND}
N 330 290 330 330 {
lab=GND}
N 320 330 330 330 {
lab=GND}
N -160 20 -160 40 {
lab=Io1}
N -340 20 -340 50 {
lab=Io1}
N -160 40 -160 50 {
lab=Io1}
N -340 190 -310 190 {
lab=I1}
N -340 170 -340 190 {
lab=I1}
N -190 190 -160 190 {
lab=#net1}
N -160 170 -160 190 {
lab=#net1}
N 150 200 200 200 {
lab=I2}
N 150 180 150 200 {
lab=I2}
N 320 200 360 200 {
lab=#net2}
N 360 180 360 200 {
lab=#net2}
C {CurrentMultiplier/LowArea_Cell.sym} -340 110 3 1 {name=x1}
C {CurrentMultiplier/LowArea_Cell.sym} -160 110 1 0 {name=x2}
C {CurrentMultiplier/LowArea_Cell.sym} 150 120 3 1 {name=x3}
C {CurrentMultiplier/LowArea_Cell.sym} 360 120 1 0 {name=x4}
C {sky130_fd_pr/pfet_01v8.sym} -230 -160 0 1 {name=M1
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
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet_01v8.sym} 230 -160 0 0 {name=M2
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
model=pfet_01v8
spiceprefix=X
}
C {devices/opin.sym} 330 -60 0 0 {name=p1 lab=Iout}
C {devices/ipin.sym} -310 210 0 0 {name=p4 lab=I1}
C {devices/ipin.sym} 200 230 0 0 {name=p6 lab=I2}
C {devices/lab_wire.sym} -250 -40 0 0 {name=p5 sig_type=std_logic lab=Io1}
C {sky130_fd_pr/nfet_01v8.sym} -210 280 0 0 {name=M3
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
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} -290 280 0 1 {name=M4
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
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 300 290 0 0 {name=M5
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
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 220 290 0 1 {name=M6
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
model=nfet_01v8
spiceprefix=X
}
C {devices/vdd.sym} 250 -210 0 0 {name=l1 lab=VDD}
C {devices/vdd.sym} -250 -210 0 0 {name=l2 lab=VDD}
C {devices/gnd.sym} -250 340 0 0 {name=l3 lab=GND}
C {devices/gnd.sym} 260 350 0 0 {name=l4 lab=GND}
