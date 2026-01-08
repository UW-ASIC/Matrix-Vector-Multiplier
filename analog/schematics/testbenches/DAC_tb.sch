v {xschem version=3.4.7 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
B 2 -810 -660 0 -250 {flags=graph
y1=-0.18026222
y2=0.84066498
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=-2.5221235e-07
x2=4.3843204e-06
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
dataset=-1
unitx=1
logx=0
logy=0
rawfile=$netlist_dir/DAC_tb.raw
color="4 5"
node="i_main
i_out_p"}
N 900 -10 900 30 {lab=#net1}
N 900 -10 940 -10 {lab=#net1}
N 1070 30 1070 50 {lab=#net2}
N 1210 -60 1270 -60 {lab=#net3}
N 1070 -220 1070 -150 {lab=#net4}
N 1070 -220 1200 -220 {lab=#net4}
N 940 -280 940 -110 {lab=#net5}
N 1260 -280 1260 -60 {lab=#net3}
N 940 -280 1070 -280 {lab=#net5}
N 1130 -280 1260 -280 {lab=#net3}
C {DAC.sym} 10 0 0 0 {name=x1}
C {devices/lab_pin.sym} 160 -120 0 1 {name=p4 lab=I_out_p}
C {sky130_fd_pr/corner.sym} 360 190 0 0 {name=CORNER only_toplevel=false corner=tt}
C {devices/launcher.sym} 490 -570 0 0 {name=h5
descr="load waves" 
tclcommand="xschem raw_read $netlist_dir/DAC_tb.raw tran"
}
C {devices/lab_pin.sym} -180 220 2 0 {name=p5 lab=V_in}
C {devices/vsource.sym} -690 -140 0 0 {name=V4 value="PULSE(0 1.8 0 100p 100p 15.15n 30.3n)" savecurrent=false}
C {devices/lab_pin.sym} -690 -170 2 0 {name=p6 lab=B0}
C {devices/gnd.sym} -690 -110 0 0 {name=l7 lab=GND}
C {devices/vsource.sym} -690 -50 0 0 {name=V5 value="PULSE(0 1.8 0 100p 100p 30.3n 60.6n)" savecurrent=false}
C {devices/lab_pin.sym} -690 -80 2 0 {name=p7 lab=B1}
C {devices/gnd.sym} -690 -20 0 0 {name=l8 lab=GND}
C {devices/vsource.sym} -690 40 0 0 {name=V6 value="PULSE(0 1.8 0 100p 100p 60.6n 121.2n)" savecurrent=false}
C {devices/lab_pin.sym} -690 10 2 0 {name=p8 lab=B2}
C {devices/gnd.sym} -690 70 0 0 {name=l9 lab=GND}
C {devices/vsource.sym} -690 130 0 0 {name=V7 value="PULSE(0 1.8 0 100p 100p 121.2n 242.4n)" savecurrent=false}
C {devices/lab_pin.sym} -690 100 2 0 {name=p9 lab=B3}
C {devices/gnd.sym} -690 160 0 0 {name=l10 lab=GND}
C {devices/vsource.sym} -690 220 0 0 {name=V8 value="PULSE(0 1.8 0 100p 100p 242.4n 484.8n)" savecurrent=false}
C {devices/lab_pin.sym} -690 190 2 0 {name=p10 lab=B4}
C {devices/gnd.sym} -690 250 0 0 {name=l11 lab=GND}
C {devices/vsource.sym} -690 310 0 0 {name=V9 value="PULSE(0 1.8 0 100p 100p 484.8n 969.6n)" savecurrent=false}
C {devices/lab_pin.sym} -690 280 2 0 {name=p11 lab=B5}
C {devices/gnd.sym} -690 340 0 0 {name=l12 lab=GND}
C {devices/vsource.sym} -690 400 0 0 {name=V10 value="PULSE(0 1.8 0 100p 100p 969.6n 1939.2n)" savecurrent=false}
C {devices/lab_pin.sym} -690 370 2 0 {name=p12 lab=B6}
C {devices/gnd.sym} -690 430 0 0 {name=l13 lab=GND}
C {devices/vsource.sym} -690 490 0 0 {name=V11 value="PULSE(0 1.8 0 100p 100p 1939.2n 3878.4n)" savecurrent=false}
C {devices/lab_pin.sym} -690 460 2 0 {name=p13 lab=B7}
C {devices/gnd.sym} -690 520 0 0 {name=l14 lab=GND}
C {devices/lab_pin.sym} -140 -160 0 0 {name=p14 lab=V_in}
C {devices/vsource.sym} -450 -140 0 0 {name=V12 value="PULSE(1.8 0 0 100p 100p 15.15n 30.3n)" savecurrent=false}
C {devices/lab_pin.sym} -450 -170 2 0 {name=p35 lab=B0_bar}
C {devices/gnd.sym} -450 -110 0 0 {name=l15 lab=GND}
C {devices/vsource.sym} -450 -50 0 0 {name=V13 value="PULSE(1.8 0 0 100p 100p 30.3n 60.6n)" savecurrent=false}
C {devices/lab_pin.sym} -450 -80 2 0 {name=p36 lab=B1_bar}
C {devices/gnd.sym} -450 -20 0 0 {name=l16 lab=GND}
C {devices/vsource.sym} -450 40 0 0 {name=V14 value="PULSE(1.8 0 0 100p 100p 60.6n 121.2n)" savecurrent=false}
C {devices/lab_pin.sym} -450 10 2 0 {name=p37 lab=B2_bar}
C {devices/gnd.sym} -450 70 0 0 {name=l17 lab=GND}
C {devices/vsource.sym} -450 130 0 0 {name=V15 value="PULSE(1.8 0 0 100p 100p 121.2n 242.4n)" savecurrent=false}
C {devices/lab_pin.sym} -450 100 2 0 {name=p38 lab=B3_bar}
C {devices/gnd.sym} -450 160 0 0 {name=l18 lab=GND}
C {devices/vsource.sym} -450 220 0 0 {name=V16 value="PULSE(1.8 0 0 100p 100p 242.4n 484.8n)" savecurrent=false}
C {devices/lab_pin.sym} -450 190 2 0 {name=p39 lab=B4_bar}
C {devices/gnd.sym} -450 250 0 0 {name=l19 lab=GND}
C {devices/vsource.sym} -450 310 0 0 {name=V17 value="PULSE(1.8 0 0 100p 100p 484.8n 969.6n)" savecurrent=false}
C {devices/lab_pin.sym} -450 280 2 0 {name=p40 lab=B5_bar}
C {devices/gnd.sym} -450 340 0 0 {name=l20 lab=GND}
C {devices/vsource.sym} -450 400 0 0 {name=V18 value="PULSE(1.8 0 0 100p 100p 969.6n 1939.2n)" savecurrent=false}
C {devices/lab_pin.sym} -450 370 2 0 {name=p41 lab=B6_bar}
C {devices/gnd.sym} -450 430 0 0 {name=l21 lab=GND}
C {devices/vsource.sym} -450 490 0 0 {name=V19 value="PULSE(1.8 0 0 100p 100p 1939.2n 3878.4n)" savecurrent=false}
C {devices/lab_pin.sym} -450 460 2 0 {name=p42 lab=B7_bar}
C {devices/gnd.sym} -450 520 0 0 {name=l22 lab=GND}
C {devices/vsource.sym} -180 250 0 0 {name=V1 value=1.8 savecurrent=false}
C {devices/gnd.sym} -180 280 0 0 {name=l1 lab=GND}
C {devices/code_shown.sym} 130 -520 0 0 {name=s1 only_toplevel=false value=".control
* Longer simulation with slower switching
tran 100p 3878.4n
* Plot differential output
let diff_out = v(I_out_p) - v(I_out_n)
plot diff_out

* Also plot individual outputs to see if one is noisier
plot v(I_out_p) v(I_out_n)

write DAC_tb.raw
.endc

.end"}
C {devices/capa.sym} 380 -130 0 0 {name=C3
m=1
value=200f
footprint=1206
device="ceramic capacitor"
spice_ignore=false}
C {devices/lab_pin.sym} 380 -160 0 1 {name=p1 lab=I_out_p
spice_ignore=false}
C {devices/gnd.sym} 380 -100 0 0 {name=l5 lab=GND
spice_ignore=false}
C {devices/lab_pin.sym} -140 -140 0 0 {name=p3 lab=B6}
C {devices/lab_pin.sym} -140 -120 0 0 {name=p15 lab=B1}
C {devices/lab_pin.sym} -140 -100 0 0 {name=p16 lab=B3}
C {devices/lab_pin.sym} -140 -80 0 0 {name=p17 lab=B4}
C {devices/lab_pin.sym} -140 -60 0 0 {name=p18 lab=B2}
C {devices/lab_pin.sym} -140 -40 0 0 {name=p19 lab=B5}
C {devices/lab_pin.sym} -140 -20 0 0 {name=p20 lab=B0}
C {devices/lab_pin.sym} -140 0 0 0 {name=p21 lab=B7}
C {devices/lab_pin.sym} -140 20 0 0 {name=p23 lab=B6_bar}
C {devices/lab_pin.sym} -140 40 0 0 {name=p25 lab=B5_bar}
C {devices/lab_pin.sym} -140 60 0 0 {name=p26 lab=B2_bar}
C {devices/lab_pin.sym} -140 80 0 0 {name=p27 lab=B1_bar}
C {devices/lab_pin.sym} -140 100 0 0 {name=p28 lab=B4_bar}
C {devices/lab_pin.sym} -140 120 0 0 {name=p29 lab=B7_bar}
C {devices/lab_pin.sym} -140 140 0 0 {name=p30 lab=B3_bar}
C {devices/lab_pin.sym} -140 160 0 0 {name=p31 lab=B0_bar}
C {devices/capa.sym} 570 -130 0 0 {name=C1
m=1
value=200f
footprint=1206
device="ceramic capacitor"
spice_ignore=false}
C {devices/lab_pin.sym} 570 -160 0 1 {name=p33 lab=I_out_n
spice_ignore=false}
C {devices/gnd.sym} 570 -100 0 0 {name=l3 lab=GND
spice_ignore=false}
C {devices/lab_pin.sym} 160 -140 0 1 {name=p34 lab=I_out_n}
C {devices/vsource.sym} 660 -130 0 0 {name=V22 value=0 savecurrent=false}
C {devices/lab_pin.sym} 660 -160 0 1 {name=p43 lab=I_out_n}
C {devices/gnd.sym} 660 -40 0 0 {name=l6 lab=GND}
C {devices/res.sym} 660 -70 0 0 {name=R3
value=1k
footprint=1206
device=resistor
m=1}
C {OpAmps/template/OpAmp.sym} 1090 -60 0 0 {name=x2
spice_ignore=true}
C {devices/lab_pin.sym} 940 -110 2 1 {name=p44 lab=I_out_p
spice_ignore=true}
C {devices/gnd.sym} 900 30 0 0 {name=l24 lab=GND
spice_ignore=true}
C {devices/gnd.sym} 1070 50 0 0 {name=l25 lab=GND
spice_ignore=true}
C {devices/vsource.sym} 1010 100 0 0 {name=V2 value=0.9 savecurrent=false
spice_ignore=true}
C {devices/gnd.sym} 1010 130 0 0 {name=l26 lab=GND
spice_ignore=true}
C {devices/vsource.sym} 1200 -190 0 0 {name=V3 value=1.8 savecurrent=false
spice_ignore=true}
C {devices/gnd.sym} 1110 -160 0 0 {name=l27 lab=GND
spice_ignore=true}
C {devices/res.sym} 1100 -280 1 0 {name=R4
value=1k
footprint=1206
device=resistor
m=1
spice_ignore=true}
C {devices/gnd.sym} 1200 -160 0 0 {name=l28 lab=GND
spice_ignore=true}
C {devices/lab_pin.sym} 1270 -60 0 1 {name=p45 lab=v_dac_out
spice_ignore=true}
C {devices/res.sym} 1260 -30 2 0 {name=R1
value=1k
footprint=1206
device=resistor
m=1
spice_ignore=true}
C {devices/vsource.sym} 440 20 0 0 {name=V21 value=0 savecurrent=false}
C {devices/lab_pin.sym} 440 -10 0 1 {name=p2 lab=I_out_p}
C {devices/gnd.sym} 440 110 0 0 {name=l2 lab=GND}
C {devices/res.sym} 440 80 0 0 {name=R2
value=1k
footprint=1206
device=resistor
m=1}
C {devices/lab_pin.sym} 440 -10 0 1 {name=p22 lab=I_out_p}
C {devices/lab_pin.sym} 160 -160 0 1 {name=p24 lab=I_main}
C {devices/lab_pin.sym} 260 -20 0 1 {name=p32 lab=I_main}
C {devices/vsource.sym} 260 10 0 0 {name=V20 value=0 savecurrent=false}
C {devices/gnd.sym} 260 100 0 0 {name=l4 lab=GND}
C {devices/res.sym} 260 70 0 0 {name=R5
value=1k
footprint=1206
device=resistor
m=1}
