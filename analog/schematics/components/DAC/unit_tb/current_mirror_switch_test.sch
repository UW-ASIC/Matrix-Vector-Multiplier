v {xschem version=3.4.7 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
B 2 570 -190 1370 210 {flags=graph
y1=-4.4366792e-08
y2=3.5368813e-08
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=4e-06
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
node=i(v12)
color=8
dataset=-1
unitx=1
logx=0
logy=0
rawfile=$netlist_dir/current_mirror_switch_test.raw}
N -30 -60 20 -60 {
lab=#net1}
N -30 40 20 40 {
lab=GND}
N -70 -30 -70 10 {
lab=#net1}
N -70 -30 -30 -30 {
lab=#net1}
N -30 -60 -30 -30 {
lab=#net1}
N -70 70 -30 70 {
lab=GND}
N -30 40 -30 70 {
lab=GND}
N 60 -30 60 10 {
lab=#net2}
N -70 -120 -70 -90 {
lab=#net3}
N -70 70 -70 110 {
lab=GND}
N 60 40 80 40 {lab=#net2}
N 80 10 80 40 {lab=#net2}
N 60 10 80 10 {lab=#net2}
N 60 -60 80 -60 {lab=V_in}
N 80 -90 80 -60 {lab=V_in}
N -90 40 -70 40 {lab=#net1}
N -90 10 -90 40 {lab=#net1}
N -90 10 -70 10 {lab=#net1}
N -90 -60 -70 -60 {lab=#net3}
N -90 -90 -90 -60 {lab=#net3}
N -90 -90 -70 -90 {lab=#net3}
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
N 20 0 20 40 {lab=GND}
N 20 -0 140 -0 {lab=GND}
N 130 0 130 40 {lab=GND}
N 170 70 170 100 {lab=#net5}
N 60 70 60 100 {lab=#net6}
N 60 160 60 210 {lab=#net7}
N 40 240 70 240 {
lab=#net7}
N 40 300 40 340 {
lab=#net8}
N 40 240 70 240 {
lab=#net7}
N 0 270 0 360 {
lab=B2_bar}
N 40 270 70 270 {lab=#net7}
N 60 240 60 270 {lab=#net7}
N 60 210 60 240 {lab=#net7}
N 70 300 70 340 {lab=#net9}
N 110 270 110 360 {lab=B2}
N 270 230 300 230 {
lab=#net10}
N 270 230 300 230 {
lab=#net10}
N 230 260 230 350 {
lab=B1_bar}
N 270 260 300 260 {lab=#net10}
N 290 230 290 260 {lab=#net10}
N 290 200 290 230 {lab=#net10}
N 300 290 300 330 {lab=#net9}
N 340 260 340 350 {lab=B1}
N 170 200 290 200 {lab=#net10}
N 170 160 170 200 {lab=#net10}
N 40 320 270 320 {lab=#net8}
N 70 330 300 330 {lab=#net9}
N 270 290 270 320 {lab=#net8}
N 290 -30 290 10 {
lab=#net11}
N 290 40 310 40 {lab=#net11}
N 310 10 310 40 {lab=#net11}
N 290 10 310 10 {lab=#net11}
N 290 -60 310 -60 {lab=V_in}
N 310 -90 310 -60 {lab=V_in}
N 290 -90 310 -90 {lab=V_in}
N 290 -120 290 -90 {lab=V_in}
N 250 -60 250 -20 {lab=#net1}
N 250 0 250 40 {lab=GND}
N 140 -0 250 -0 {lab=GND}
N 140 -20 250 -20 {lab=#net1}
N 480 230 510 230 {
lab=#net12}
N 480 230 510 230 {
lab=#net12}
N 440 260 440 350 {
lab=B0_bar}
N 480 260 510 260 {lab=#net12}
N 500 230 500 260 {lab=#net12}
N 510 290 510 330 {lab=#net9}
N 550 260 550 350 {lab=B0}
N 480 290 480 320 {lab=#net8}
N 270 320 480 320 {lab=#net8}
N 300 330 510 330 {lab=#net9}
N 500 160 500 230 {lab=#net12}
N 290 160 500 160 {lab=#net12}
N 40 400 40 460 {lab=GND}
N 1080 610 1140 610 {lab=#net13}
N 940 460 940 520 {lab=#net14}
N 940 460 1090 460 {lab=#net14}
N 1130 390 1130 610 {lab=#net13}
N 1030 390 1130 390 {lab=#net13}
N 810 390 810 560 {lab=#net15}
N 810 390 970 390 {lab=#net15}
N 750 660 750 710 {lab=GND}
N 750 660 810 660 {lab=GND}
N 290 70 290 100 {lab=#net16}
C {sky130_fd_pr/pfet_01v8.sym} 40 -60 0 0 {name=M1
W=min_width
L=length
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
L=length
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
L=length
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
L=length
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
C {devices/lab_pin.sym} 60 -120 2 0 {name=p2 sig_type=std_logic lab=V_in
L=length}
C {devices/lab_pin.sym} -310 -60 2 0 {name=p3 sig_type=std_logic lab=V_in}
C {sky130_fd_pr/pfet_01v8.sym} 150 -60 0 0 {name=M5
W=min_width
L=length
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
L=length
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
C {devices/lab_pin.sym} 170 -120 2 0 {name=p1 sig_type=std_logic lab=V_in
L=length}
C {devices/code_shown.sym} -107.5 627.5 0 0 {name=s1 only_toplevel=false value=".param min_width=0.42
.param switch_multiplier=1
.param length=0.425
.param i_bias=8u
.control
tran 50p 4u
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
C {devices/vsource.sym} -310 -30 0 0 {name=V7 value=1.8 savecurrent=false}
C {devices/vsource.sym} 170 130 0 0 {name=V8 value=0 savecurrent=false
L=length}
C {sky130_fd_pr/pfet_01v8.sym} 20 270 0 0 {name=M12
W=min_width
L=length
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
W=min_width
L=length
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
C {devices/vsource.sym} 60 130 0 0 {name=V10 value=0 savecurrent=false
L=length}
C {devices/vsource.sym} 40 370 0 0 {name=V11 value=0 savecurrent=false
L=length}
C {devices/vsource.sym} 70 370 0 0 {name=V12 value=0 savecurrent=false
L=length}
C {sky130_fd_pr/pfet_01v8.sym} 250 260 0 0 {name=M7
W=min_width
L=length
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
W=min_width
L=length
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
L=length}
C {devices/lab_pin.sym} 340 350 2 0 {name=p8 sig_type=std_logic lab=B1
L=length}
C {devices/lab_pin.sym} 70 400 0 1 {name=p22 lab=I_out_p
L=length}
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
L=length
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
L=length
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
C {devices/lab_pin.sym} 290 -120 2 0 {name=p18 sig_type=std_logic lab=V_in
L=length}
C {devices/vsource.sym} 290 130 0 0 {name=V13 value=0 savecurrent=false
L=length}
C {devices/lab_pin.sym} 550 350 2 0 {name=p19 sig_type=std_logic lab=B0
L=length}
C {devices/lab_pin.sym} 440 350 0 0 {name=p20 sig_type=std_logic lab=B0_bar
L=length}
C {sky130_fd_pr/pfet_01v8.sym} 460 260 0 0 {name=M11
W=min_width
L=length
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
W=min_width
L=length
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
L=length}
C {devices/lab_pin.sym} 0 360 0 0 {name=p7 sig_type=std_logic lab=B2_bar
L=length}
C {devices/launcher.sym} 690 247.5 0 0 {name=h5
descr="load waves" 
tclcommand="xschem raw_read $netlist_dir/current_mirror_switch_test.raw tran"}
C {devices/gnd.sym} -70 110 0 0 {name=l13 lab=GND
L=length}
C {devices/isource.sym} -70 -150 0 0 {name=I0 value=i_bias}
C {devices/gnd.sym} 40 460 0 0 {name=l1 lab=GND
L=length}
C {devices/lab_pin.sym} 750 560 2 1 {name=p44 lab=I_out_p
spice_ignore=false}
C {devices/vsource.sym} 1090 490 0 0 {name=V14 value=1.8 savecurrent=false
spice_ignore=false}
C {devices/gnd.sym} 1090 520 0 0 {name=l28 lab=GND
spice_ignore=false}
C {devices/lab_pin.sym} 1200 610 0 1 {name=p45 lab=v_dac_out
spice_ignore=false}
C {devices/res.sym} 1130 640 2 0 {name=R1
value=1k
footprint=1206
device=resistor
m=1
spice_ignore=false}
C {devices/gnd.sym} 1130 670 0 0 {name=l4 lab=GND
spice_ignore=false}
C {devices/vsource.sym} 780 560 3 0 {name=V31 value=0 savecurrent=false}
C {OpAmp/Two-Stage_Miller/OpAmp.sym} 960 610 0 0 {name=x2}
C {devices/res.sym} 1000 390 3 0 {name=R3
value=1k
footprint=1206
device=resistor
m=1
spice_ignore=false}
C {devices/gnd.sym} 750 710 0 0 {name=l10 lab=GND}
C {devices/vsource.sym} 880 770 0 0 {name=V15 value=0.9 savecurrent=false}
C {devices/gnd.sym} 880 800 0 0 {name=l14 lab=GND}
C {devices/gnd.sym} 940 700 0 0 {name=l15 lab=GND}
C {devices/res.sym} 1170 610 3 0 {name=R4
value=200
footprint=1206
device=resistor
m=1
spice_ignore=false}
C {devices/capa.sym} 1200 640 2 0 {name=C1
m=1
value=1p
footprint=1206
device="ceramic capacitor"}
C {devices/gnd.sym} 1200 670 0 0 {name=l31 lab=GND
spice_ignore=false}
C {devices/lab_pin.sym} -70 -180 2 0 {name=p5 sig_type=std_logic lab=V_in}
