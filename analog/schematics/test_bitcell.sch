v {xschem version=3.4.7 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N -80 -0 -60 0 {lab=#net1}
N -0 60 0 80 {lab=#net2}
N 0 -80 -0 -50 {lab=#net3}
N 50 0 100 0 {lab=#net4}
N -150 -0 -140 -0 {lab=GND}
N 100 -0 130 0 {lab=#net4}
N 130 0 150 0 {lab=#net4}
N 120 100 120 130 {lab=#net5}
N 60 100 120 100 {lab=#net5}
N 60 30 60 100 {lab=#net5}
C {Core/BitCell_2T1C.sym} 0 10 0 0 {name=x1}
C {devices/vsource.sym} -110 0 1 0 {name=V1 value="PWL(0n 0 10n 0 10.1n 1.8 110n 1.8 110.1n 0 200n 0)" savecurrent=false}
C {devices/vsource.sym} 0 -110 2 0 {name=V3 value="PWL(0n 0 10n 0 10.1n 1.8 30n 1.8 30.1n 0 200n 0)" savecurrent=false}
C {devices/code_shown.sym} 600 -280 0 0 {name=s1 only_toplevel=false value="""
.param V_WWL=1.8
.param V_RWL=1.8
.param V_WBL=1.8
.param V_LSB='1.8/4'

.save v(net4) v(net1) v(net2) v(net3) v(x1.net1) v(pre)

.tran 0.01n 200n

** Write: target = 90% of actual peak (~1.0V), so 0.9
.meas tran t_write1 TRIG V(net1) VAL=0.9 RISE=1 TARG V(x1.net1) VAL=0.9 RISE=1

** Read: target = 50% of actual RBL swing (~0.43V), so 0.2
.meas tran t_read1 TRIG V(net2) VAL=0.9 RISE=1 TARG V(net4) VAL=0.2 RISE=1

** Retention: check when storage drops from peak by V_LSB/2
** Peak is ~1.05V now, so target = 1.05 - 0.056 = 0.994
.meas tran t_retain TRIG AT=31n TARG V(x1.net1) VAL=0.994 FALL=1

** Also add a measurement to capture the actual peak
.meas tran V_store_peak MAX V(x1.net1) FROM=25n TO=35n

.control
save all
run
write test_bitcell.raw
.endc
"""}
C {devices/gnd.sym} 0 140 0 0 {name=l1 lab=GND}
C {devices/gnd.sym} -150 0 0 0 {name=l2 lab=GND}
C {devices/gnd.sym} 0 -140 2 0 {name=l3 lab=GND}
C {devices/capa.sym} 150 30 0 0 {name=C1
m=1
value=50f
footprint=1206
device="ceramic capacitor"}
C {devices/gnd.sym} 150 60 0 0 {name=l4 lab=GND}
C {devices/vsource.sym} 0 110 0 0 {name=V2 value="PWL(0n 0 40n 0 40.1n 1.8 60n 1.8 60.1n 0 80n 0 80.1n 1.8 100n 1.8 100.1n 0 200n 0)" savecurrent=false}
C {sky130_fd_pr/corner.sym} 300 -230 0 0 {name=CORNER only_toplevel=false corner=tt}
C {devices/gnd.sym} 100 60 0 0 {name=l5 lab=GND}
C {devices/vsource.sym} 120 160 0 0 {name=V4 value="PWL(0n 0 35n 0 35.1n 1.8 39n 1.8 39.1n 0 75n 0 75.1n 1.8 79n 1.8 79.1n 0 200n 0)" savecurrent=false}
C {devices/gnd.sym} 120 190 0 0 {name=l6 lab=GND}
C {sky130_fd_pr/nfet3_01v8.sym} 80 30 0 0 {name=M1
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
