v {xschem version=3.4.7 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
B 2 570 -190 1370 210 {flags=graph
y1=-0.042385425
y2=0.049723722
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=-3.2222215e-06
x2=1.202396e-05
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
node="i(v10)
i(v8)
i(v13)
i_out_p"
color="8 7 4 18"
dataset=-1
unitx=1
logx=0
logy=0
rawfile=$netlist_dir/current_mirror_switch_test.raw}
N -30 -60 20 -60 {
lab=#net1}
N -30 40 20 40 {
lab=#net2}
N -70 -30 -70 10 {
lab=#net1}
N -70 -30 -30 -30 {
lab=#net1}
N -30 -60 -30 -30 {
lab=#net1}
N -70 70 -30 70 {
lab=#net2}
N -30 40 -30 70 {
lab=#net2}
N 60 -30 60 10 {
lab=#net3}
N -70 -120 -70 -90 {
lab=V_in}
N -70 70 -70 110 {
lab=#net2}
N 60 40 80 40 {lab=#net3}
N 80 10 80 40 {lab=#net3}
N 60 10 80 10 {lab=#net3}
N 60 -60 80 -60 {lab=V_in}
N 80 -90 80 -60 {lab=V_in}
N -90 40 -70 40 {lab=#net1}
N -90 10 -90 40 {lab=#net1}
N -90 10 -70 10 {lab=#net1}
N -90 -60 -70 -60 {lab=V_in}
N -90 -90 -90 -60 {lab=V_in}
N -90 -90 -70 -90 {lab=V_in}
N 60 -90 80 -90 {lab=V_in}
N 60 -120 60 -90 {lab=V_in}
N 170 -30 170 10 {
lab=#net4}
N 170 40 190 40 {lab=#net4}
N 190 10 190 40 {lab=#net4}
N 170 10 190 10 {lab=#net4}
N 170 -60 190 -60 {lab=V_in}
N 190 -90 190 -60 {lab=V_in}
N 170 -90 190 -90 {lab=V_in}
N 170 -120 170 -90 {lab=V_in}
N 20 -60 20 -20 {lab=#net1}
N 20 -20 140 -20 {lab=#net1}
N 130 -60 130 -20 {lab=#net1}
N 20 0 20 40 {lab=#net2}
N 20 -0 140 -0 {lab=#net2}
N 130 0 130 40 {lab=#net2}
N 170 70 170 100 {lab=#net5}
N 60 70 60 100 {lab=#net6}
N 60 160 60 210 {lab=#net7}
N 40 240 70 240 {
lab=#net7}
N 40 300 40 340 {
lab=I_out_n}
N 40 240 70 240 {
lab=#net7}
N 0 270 0 360 {
lab=B2_bar}
N 40 270 70 270 {lab=#net7}
N 60 240 60 270 {lab=#net7}
N 60 210 60 240 {lab=#net7}
N 70 300 70 340 {lab=I_out_p}
N 110 270 110 360 {lab=B2}
N 270 230 300 230 {
lab=#net8}
N 270 230 300 230 {
lab=#net8}
N 230 260 230 350 {
lab=B1_bar}
N 270 260 300 260 {lab=#net8}
N 290 230 290 260 {lab=#net8}
N 290 200 290 230 {lab=#net8}
N 300 290 300 330 {lab=I_out_p}
N 340 260 340 350 {lab=B1}
N 170 200 290 200 {lab=#net8}
N 170 160 170 200 {lab=#net8}
N 40 320 270 320 {lab=I_out_n}
N 70 330 300 330 {lab=I_out_p}
N 270 290 270 320 {lab=I_out_n}
N 290 -30 290 10 {
lab=#net9}
N 290 40 310 40 {lab=#net9}
N 310 10 310 40 {lab=#net9}
N 290 10 310 10 {lab=#net9}
N 290 -60 310 -60 {lab=V_in}
N 310 -90 310 -60 {lab=V_in}
N 290 -90 310 -90 {lab=V_in}
N 290 -120 290 -90 {lab=V_in}
N 250 -60 250 -20 {lab=#net1}
N 250 0 250 40 {lab=#net2}
N 290 70 290 100 {lab=#net10}
N 140 -0 250 -0 {lab=#net2}
N 140 -20 250 -20 {lab=#net1}
N 480 230 510 230 {
lab=#net11}
N 480 230 510 230 {
lab=#net11}
N 440 260 440 350 {
lab=B0_bar}
N 480 260 510 260 {lab=#net11}
N 500 230 500 260 {lab=#net11}
N 510 290 510 330 {lab=I_out_p}
N 550 260 550 350 {lab=B0}
N 480 290 480 320 {lab=I_out_n}
N 270 320 480 320 {lab=I_out_n}
N 300 330 510 330 {lab=I_out_p}
N 500 160 500 230 {lab=#net11}
N 290 160 500 160 {lab=#net11}
N -132.5 502.5 -132.5 507.5 {lab=GND}
C {sky130_fd_pr/pfet_01v8.sym} 40 -60 0 0 {name=M1
W=min_width
L=0.15
nf=1
mult=4
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet_01v8.sym} 40 40 0 0 {name=M2
W=min_width
L=0.15
nf=1
mult=4
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet_01v8.sym} -50 -60 0 1 {name=M3
W=min_width
L=0.15
nf=1
mult=4
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet_01v8.sym} -50 40 0 1 {name=M4
W=min_width
L=0.15
nf=1
mult=4
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
C {devices/lab_pin.sym} 60 -120 2 0 {name=p2 sig_type=std_logic lab=V_in}
C {devices/lab_pin.sym} -310 -60 2 0 {name=p3 sig_type=std_logic lab=V_in}
C {devices/res.sym} -70 200 0 0 {name=R1
value=1k
footprint=1206
device=resistor
m=1}
C {sky130_fd_pr/pfet_01v8.sym} 150 -60 0 0 {name=M5
W=min_width
L=0.15
nf=1
mult=2
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet_01v8.sym} 150 40 0 0 {name=M6
W=min_width
L=0.15
nf=1
mult=2
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
C {devices/lab_pin.sym} 170 -120 2 0 {name=p1 sig_type=std_logic lab=V_in}
C {devices/lab_pin.sym} -70 -120 2 0 {name=p5 sig_type=std_logic lab=V_in}
C {devices/code_shown.sym} -107.5 630 0 0 {name=s1 only_toplevel=false value=".param min_width=0.6
.param switch_multiplier=0.8
.control
tran 1n 8u
write current_mirror_switch_test.raw
.endc
.end"}
C {sky130_fd_pr/corner.sym} 260 670 0 0 {name=CORNER only_toplevel=false corner=tt}
C {devices/vsource.sym} -530 170 0 0 {name=V2 value="PULSE(0 1.8 0 100p 100p 500n 1u)" savecurrent=false
}
C {devices/gnd.sym} -530 200 0 0 {name=l5 lab=GND
}
C {devices/vsource.sym} -470 170 0 0 {name=V3 value="PULSE(1.8 0 0 100p 100p 500n 1u)" savecurrent=false
}
C {devices/gnd.sym} -470 200 0 0 {name=l6 lab=GND
}
C {devices/vsource.sym} -530 280 0 0 {name=V4 value="PULSE(0 1.8 0 100p 100p 1u 2u)" savecurrent=false
}
C {devices/gnd.sym} -530 310 0 0 {name=l7 lab=GND
}
C {devices/vsource.sym} -470 280 0 0 {name=V5 value="PULSE(1.8 0 0 100p 100p 1u 2u)" savecurrent=false
}
C {devices/gnd.sym} -470 310 0 0 {name=l8 lab=GND
}
C {devices/lab_pin.sym} -530 140 2 0 {name=p10 sig_type=std_logic lab=B0
}
C {devices/lab_pin.sym} -470 140 2 0 {name=p11 sig_type=std_logic lab=B0_bar
}
C {devices/lab_pin.sym} -530 250 2 0 {name=p12 sig_type=std_logic lab=B1
}
C {devices/lab_pin.sym} -470 250 2 0 {name=p13 sig_type=std_logic lab=B1_bar
}
C {devices/gnd.sym} -310 0 0 0 {name=l9 lab=GND}
C {devices/gnd.sym} -70 230 0 0 {name=l1 lab=GND}
C {devices/vsource.sym} -310 -30 0 0 {name=V7 value=1.8 savecurrent=false}
C {devices/vsource.sym} 170 130 0 0 {name=V8 value=0 savecurrent=false}
C {devices/vsource.sym} -70 140 0 0 {name=V1 value=0 savecurrent=false}
C {sky130_fd_pr/pfet_01v8.sym} 20 270 0 0 {name=M12
W=min_width*switch_multiplier
L=0.15
nf=1
mult=4
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet_01v8.sym} 90 270 0 1 {name=M13
W=min_width*switch_multiplier
L=0.15
nf=1
mult=4
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
C {devices/gnd.sym} 40 460 0 0 {name=l2 lab=GND}
C {devices/res.sym} 70 430 0 0 {name=R4
value=1k
footprint=1206
device=resistor
m=1}
C {devices/gnd.sym} 70 460 0 0 {name=l3 lab=GND}
C {devices/vsource.sym} 60 130 0 0 {name=V10 value=0 savecurrent=false}
C {devices/vsource.sym} 40 370 0 0 {name=V11 value=0 savecurrent=false}
C {devices/vsource.sym} 70 370 0 0 {name=V12 value=0 savecurrent=false}
C {sky130_fd_pr/pfet_01v8.sym} 250 260 0 0 {name=M7
W=min_width*switch_multiplier
L=0.15
nf=1
mult=2
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet_01v8.sym} 320 260 0 1 {name=M8
W=min_width*switch_multiplier
L=0.15
nf=1
mult=2
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
C {devices/lab_pin.sym} 230 350 0 0 {name=p4 sig_type=std_logic lab=B1_bar
}
C {devices/lab_pin.sym} 340 350 2 0 {name=p8 sig_type=std_logic lab=B1
}
C {devices/lab_pin.sym} 300 310 0 1 {name=p22 lab=I_out_p}
C {devices/lab_pin.sym} 260 320 1 1 {name=p9 lab=I_out_n}
C {devices/lab_pin.sym} -70 170 0 1 {name=p24 lab=I_main}
C {devices/vsource.sym} -530 390 0 0 {name=V6 value="PULSE(0 1.8 0 100p 100p 2u 4u)" savecurrent=false
}
C {devices/gnd.sym} -530 420 0 0 {name=l11 lab=GND
}
C {devices/vsource.sym} -470 390 0 0 {name=V9 value="PULSE(1.8 0 0 100p 100p 2u 4u)" savecurrent=false
}
C {devices/gnd.sym} -470 420 0 0 {name=l12 lab=GND
}
C {devices/lab_pin.sym} -530 360 2 0 {name=p16 sig_type=std_logic lab=B2
}
C {devices/lab_pin.sym} -470 360 2 0 {name=p17 sig_type=std_logic lab=B2_bar
}
C {sky130_fd_pr/pfet_01v8.sym} 270 -60 0 0 {name=M9
W=min_width
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
C {sky130_fd_pr/pfet_01v8.sym} 270 40 0 0 {name=M10
W=min_width
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
C {devices/lab_pin.sym} 290 -120 2 0 {name=p18 sig_type=std_logic lab=V_in}
C {devices/vsource.sym} 290 130 0 0 {name=V13 value=0 savecurrent=false}
C {devices/lab_pin.sym} 550 350 2 0 {name=p19 sig_type=std_logic lab=B0
}
C {devices/lab_pin.sym} 440 350 0 0 {name=p20 sig_type=std_logic lab=B0_bar
}
C {sky130_fd_pr/pfet_01v8.sym} 460 260 0 0 {name=M11
W=min_width*switch_multiplier
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
C {sky130_fd_pr/pfet_01v8.sym} 530 260 0 1 {name=M14
W=min_width*switch_multiplier
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
C {devices/lab_pin.sym} 110 360 2 0 {name=p6 sig_type=std_logic lab=B2
}
C {devices/lab_pin.sym} 0 360 0 0 {name=p7 sig_type=std_logic lab=B2_bar
}
C {devices/res.sym} 40 430 0 0 {name=R2
value=1k
footprint=1206
device=resistor
m=1}
C {devices/launcher.sym} 690 247.5 0 0 {name=h5
descr="load waves" 
tclcommand="xschem raw_read $netlist_dir/current_mirror_switch_test.raw tran"}
C {devices/capa.sym} -132.5 472.5 0 0 {name=C3
m=1
value=2p
footprint=1206
device="ceramic capacitor"
spice_ignore=false}
C {devices/lab_pin.sym} -132.5 442.5 0 1 {name=p14 lab=I_out_p}
C {devices/gnd.sym} -132.5 507.5 0 0 {name=l4 lab=GND}
