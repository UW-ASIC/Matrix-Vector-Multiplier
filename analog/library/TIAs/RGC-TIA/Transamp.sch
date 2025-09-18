v {xschem version=3.4.4 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N -140 140 -120 140 {
lab=Iin}
N -120 140 -120 180 {
lab=Iin}
N -140 180 -120 180 {
lab=Iin}
N -140 170 -140 180 {
lab=Iin}
N -140 180 -140 250 {
lab=Iin}
N -0 210 20 210 {
lab=Vss}
N 20 210 20 250 {
lab=Vss}
N -0 250 20 250 {
lab=Vss}
N 0 240 0 250 {
lab=Vss}
N -140 310 -140 330 {
lab=Vss}
N 0 250 -0 330 {
lab=Vss}
N -140 -30 -140 110 {
lab=#net1}
N -140 60 100 60 {
lab=#net1}
N 0 -30 -0 180 {
lab=#net2}
N -140 210 -40 210 {
lab=Iin}
N -140 -120 -140 -90 {
lab=Vdd}
N 0 -120 0 -90 {
lab=Vdd}
N 0 -140 0 -120 {
lab=Vdd}
N -160 210 -140 210 {
lab=Iin}
N -200 140 -180 140 {
lab=#net2}
N -200 80 -200 140 {
lab=#net2}
N -200 80 -0 80 {
lab=#net2}
N 0 330 -0 350 {
lab=Vss}
N -140 -120 0 -120 {
lab=Vdd}
N -140 330 0 330 {
lab=Vss}
N 280 310 280 330 {
lab=Vss}
N -0 330 280 330 {
lab=Vss}
N 140 310 140 330 {
lab=Vss}
N 140 90 140 250 {
lab=#net3}
N 280 230 280 250 {
lab=#net3}
N 140 230 280 230 {
lab=#net3}
N 140 -30 140 30 {
lab=Vout}
N 140 -0 180 -0 {
lab=Vout}
N 140 -120 140 -90 {
lab=Vdd}
N -0 -120 140 -120 {
lab=Vdd}
N 140 60 160 60 {}
N 160 60 160 100 {}
N 140 100 160 100 {}
C {sky130_fd_pr/res_generic_l1.sym} -140 -60 0 0 {name=R1
W=0.20
L=32.8
model=res_generic_l1
mult=1}
C {sky130_fd_pr/res_generic_l1.sym} 0 -60 0 0 {name=R2
W=0.20
L=32.8
model=res_generic_l1
mult=1}
C {sky130_fd_pr/res_generic_l1.sym} -140 280 0 0 {name=R4
W=0.20
L=32.8
model=res_generic_l1
mult=1}
C {ipin.sym} -160 210 0 0 {name=p1 lab=Iin}
C {opin.sym} 180 0 0 0 {name=p2 lab=Vout}
C {iopin.sym} 0 350 1 0 {name=p3 lab=Vss}
C {iopin.sym} 0 -140 3 0 {name=p4 lab=Vdd}
C {sky130_fd_pr/nfet_01v8_lvt_nf.sym} -160 140 0 0 {name=M1
W=12.5
L=0.5
nf=10
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8_lvt
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8_lvt_nf.sym} -20 210 0 0 {name=M2
W=12.5
L=0.5
nf=10
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8_lvt
spiceprefix=X
}
C {sky130_fd_pr/res_generic_l1.sym} 140 -60 0 0 {name=R3
W=0.20
L=98.3
model=res_generic_l1
mult=1}
C {sky130_fd_pr/nfet_01v8_lvt_nf.sym} 120 60 0 0 {name=M3
W=12.5
L=0.5
nf=10
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8_lvt
spiceprefix=X
}
C {sky130_fd_pr/res_generic_l1.sym} 140 280 0 0 {name=R5
W=0.20
L=96.6
model=res_generic_l1
mult=1}
C {sky130_fd_pr/cap_mim_m3_1.sym} 280 280 0 0 {name=C1 model=cap_mim_m3_1 W=12 L=6 MF=3 spiceprefix=X}
