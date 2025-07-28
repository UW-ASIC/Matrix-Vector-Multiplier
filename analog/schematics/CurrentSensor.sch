v {xschem version=3.4.4 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
T {R1 = (Vout_max - Vout_min) / Iin_max
R1 = (1.8V - 0V) / 50uA      // Assuming current
R1 = 24kOhm} 220 -400 0 0 0.2 0.2 {}
T {C1 ≤ 1 / (2π × R1 × f_bandwidth)
C1 ≤ 1 / (2π x 24k x 100MHz)
C1 < 0.066pF} 220 -330 0 0 0.2 0.2 {}
T {https://www.ti.com/lit/an/sboa268b/sboa268b.pdf?ts=1753598050348} 220 -420 0 0 0.2 0.2 {}
N -100 -210 -100 -50 {
lab=Iin}
N -100 -210 -10 -210 {
lab=Iin}
N -100 -380 -100 -210 {
lab=Iin}
N -100 -380 -0 -380 {
lab=Iin}
N 170 -210 170 0 {
lab=Vout}
N 50 -210 170 -210 {
lab=Vout}
N 60 -380 170 -380 {
lab=Vout}
N 170 -380 170 -210 {
lab=Vout}
N -130 50 -100 50 {
lab=GND}
N -130 50 -130 70 {
lab=GND}
N 170 0 260 -0 {
lab=Vout}
N -140 -50 -100 -50 {
lab=Iin}
C {Operational_Amplifiers/OpAmp.sym} 50 0 0 0 {name=x1}
C {devices/vdd.sym} 30 -90 0 0 {name=l1 lab=VDD}
C {devices/gnd.sym} 30 90 0 0 {name=l2 lab=GND}
C {devices/vsource.sym} -30 160 0 0 {name=V1 value=3 savecurrent=false}
C {devices/gnd.sym} -30 190 0 0 {name=l3 lab=GND}
C {sky130_fd_pr/cap_mim_m3_1.sym} 30 -380 3 0 {name=C1 model=cap_mim_m3_1 W=1 L=1 MF=1 spiceprefix=X}
C {devices/gnd.sym} -130 70 0 0 {name=l4 lab=GND}
C {devices/ipin.sym} -140 -50 0 0 {name=p1 lab=Iin}
C {devices/opin.sym} 260 0 0 0 {name=p2 lab=Vout}
C {sky130_fd_pr/res_xhigh_po_5p73.sym} 20 -210 3 0 {name=R2
L=5.73
model=res_xhigh_po_5p73
spiceprefix=X
mult=1}
C {devices/gnd.sym} 20 -190 0 0 {name=l5 lab=GND}
