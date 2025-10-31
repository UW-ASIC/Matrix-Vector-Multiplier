v {xschem version=3.4.4 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N -160 0 -100 0 {
lab=#net1}
N -160 -20 -100 -20 {
lab=#net2}
N 110 -10 140 -10 {
lab=#net3}
N -30 -170 -30 -150 {
lab=VSS}
N -90 -170 -90 -150 {
lab=VDD}
C {CurrentMultiplier/CurrentMultiplier_LowArea.sym} 0 0 0 0 {name=x1}
C {devices/isource.sym} -190 -20 3 0 {name=I1 value=2.5u}
C {devices/isource.sym} -190 0 3 0 {name=I2 value=1.5u}
C {devices/code_shown.sym} 300 -50 0 0 {name=s1 only_toplevel=false value="""
.control
save all
op
print i(Vmeas)
print v(net1) v(net2) v(net3)
* Measure resistance indirectly: R = V/I
print v(x.x1.x1.iin) v(x.x1.x1.gnd)
print i(v.x1.x1.xr1)
* Or try different syntax for subcircuit resistor
print @x.x1.x1.xr1.xsky130_fd_pr__res_high_po_5p73[resistance]
* Transistor parameters from LowArea_Cell
print @m.x1.x1.xm1.msky130_fd_pr__nfet_01v8_lvt[gm]
print @m.x1.x1.xm1.msky130_fd_pr__nfet_01v8_lvt[vth]
print @m.x1.x1.xm1.msky130_fd_pr__nfet_01v8_lvt[vdsat]
print @m.x1.x1.xm1.msky130_fd_pr__nfet_01v8_lvt[id]
* Calculate Ix and Iy
print (2.5e-6+1.5e-6)/2
print (2.5e-6-1.5e-6)/2
.endc
"""}
C {sky130_fd_pr/corner.sym} 180 -290 0 0 {name=CORNER only_toplevel=false corner=tt}
C {devices/vsource.sym} 170 -10 3 0 {name=Vmeas value=0V savecurrent=false}
C {devices/vdd.sym} -90 -170 0 0 {name=l1 lab=VDD}
C {devices/gnd.sym} -30 -170 2 0 {name=l2 lab=VSS}
C {devices/vsource.sym} -90 -120 0 0 {name=V1 value=1.8V savecurrent=false}
C {devices/vsource.sym} -30 -120 0 0 {name=V2 value=-1.8V savecurrent=false}
C {devices/gnd.sym} -90 -90 0 0 {name=l5 lab=GND}
C {devices/gnd.sym} -30 -90 0 0 {name=l6 lab=GND}
C {devices/vdd.sym} -220 -20 0 0 {name=l7 lab=VDD}
C {devices/vdd.sym} -220 0 0 0 {name=l8 lab=VDD}
C {devices/gnd.sym} 200 -10 0 0 {name=l3 lab=GND}
