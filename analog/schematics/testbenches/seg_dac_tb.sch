v {xschem version=3.4.7 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
B 2 -850 -690 -50 -290 {flags=graph
y1=-2.0701085e-06
y2=1.0537798e-06
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=8.2961566e-09
x2=3.2803862e-08
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
node="v_dac_out_p
i(v31)"
color="4 10"
dataset=-1
unitx=1
logx=0
logy=0
}
N 620 -140 620 -100 {lab=GND}
N 620 -140 660 -140 {lab=GND}
N 790 -100 790 -80 {lab=GND}
N 930 -190 990 -190 {lab=v_dac_out_p}
N 790 -350 790 -280 {lab=#net1}
N 790 -350 920 -350 {lab=#net1}
N 660 -410 660 -240 {lab=#net2}
N 980 -410 980 -190 {lab=v_dac_out_p}
N 660 -410 790 -410 {lab=#net2}
N 850 -410 980 -410 {lab=v_dac_out_p}
N 620 340 620 380 {lab=GND}
N 620 340 660 340 {lab=GND}
N 790 380 790 400 {lab=GND}
N 790 130 790 200 {lab=#net3}
N 790 130 920 130 {lab=#net3}
N 660 70 660 240 {lab=I_out_n}
N 980 70 980 290 {lab=v_dac_out_n}
N 660 70 790 70 {lab=I_out_n}
N 850 70 980 70 {lab=v_dac_out_n}
N 930 290 990 290 {lab=v_dac_out_n}
N 790 130 920 130 {lab=#net3}
C {segmented_dac.sym} 20 0 0 0 {name=x1}
C {devices/lab_pin.sym} -130 -240 0 0 {name=p1 lab=V_in}
C {devices/lab_pin.sym} 170 -240 0 1 {name=p2 lab=I_main}
C {devices/lab_pin.sym} 170 -220 0 1 {name=p3 lab=I_out_n}
C {devices/lab_pin.sym} 170 -200 0 1 {name=p4 lab=I_out_p}
C {devices/lab_pin.sym} -130 -220 0 0 {name=p5 lab=T1}
C {devices/lab_pin.sym} -130 -200 0 0 {name=p6 lab=T3}
C {devices/lab_pin.sym} -130 -180 0 0 {name=p7 lab=T4}
C {devices/lab_pin.sym} -130 -160 0 0 {name=p8 lab=B3}
C {devices/lab_pin.sym} -130 -140 0 0 {name=p9 lab=T2}
C {devices/lab_pin.sym} -130 -120 0 0 {name=p10 lab=T0}
C {devices/lab_pin.sym} -130 -100 0 0 {name=p11 lab=B4}
C {devices/lab_pin.sym} -130 -80 0 0 {name=p12 lab=T5}
C {devices/lab_pin.sym} -130 -60 0 0 {name=p13 lab=B2}
C {devices/lab_pin.sym} -130 -40 0 0 {name=p14 lab=B0}
C {devices/lab_pin.sym} -130 -20 0 0 {name=p15 lab=T6}
C {devices/lab_pin.sym} -130 0 0 0 {name=p16 lab=B1}
C {devices/lab_pin.sym} -130 20 0 0 {name=p17 lab=T1_n}
C {devices/lab_pin.sym} -130 40 0 0 {name=p18 lab=T0_n}
C {devices/lab_pin.sym} -130 60 0 0 {name=p19 lab=B2_n}
C {devices/lab_pin.sym} -130 80 0 0 {name=p20 lab=T5_n}
C {devices/lab_pin.sym} -130 100 0 0 {name=p21 lab=T4_n}
C {devices/lab_pin.sym} -130 120 0 0 {name=p22 lab=T3_n}
C {devices/lab_pin.sym} -130 140 0 0 {name=p23 lab=B1_n}
C {devices/lab_pin.sym} -130 160 0 0 {name=p24 lab=B4_n}
C {devices/lab_pin.sym} -130 180 0 0 {name=p25 lab=T2_n}
C {devices/lab_pin.sym} -130 200 0 0 {name=p26 lab=B3_n}
C {devices/lab_pin.sym} -130 220 0 0 {name=p27 lab=T6_n}
C {devices/lab_pin.sym} -130 240 0 0 {name=p28 lab=B0_n}
C {devices/vsource.sym} -690 -140 0 0 {name=V4 value="PULSE(0 1.8 0 100p 100p 15.15n 30.3n)" savecurrent=false}
C {devices/lab_pin.sym} -690 -170 2 0 {name=p30 lab=B0}
C {devices/gnd.sym} -690 -110 0 0 {name=l7 lab=GND}
C {devices/vsource.sym} -690 -50 0 0 {name=V5 value="PULSE(0 1.8 0 100p 100p 30.3n 60.6n)" savecurrent=false}
C {devices/lab_pin.sym} -690 -80 2 0 {name=p31 lab=B1}
C {devices/gnd.sym} -690 -20 0 0 {name=l8 lab=GND}
C {devices/vsource.sym} -690 40 0 0 {name=V6 value="PULSE(0 1.8 0 100p 100p 60.6n 121.2n)" savecurrent=false}
C {devices/lab_pin.sym} -690 10 2 0 {name=p32 lab=B2}
C {devices/gnd.sym} -690 70 0 0 {name=l9 lab=GND}
C {devices/vsource.sym} -690 130 0 0 {name=V7 value="PULSE(0 1.8 0 100p 100p 121.2n 242.4n)" savecurrent=false}
C {devices/lab_pin.sym} -690 100 2 0 {name=p33 lab=B3}
C {devices/gnd.sym} -690 160 0 0 {name=l10 lab=GND}
C {devices/vsource.sym} -690 220 0 0 {name=V8 value="PULSE(0 1.8 0 100p 100p 242.4n 484.8n)" savecurrent=false}
C {devices/lab_pin.sym} -690 190 2 0 {name=p34 lab=B4}
C {devices/gnd.sym} -690 250 0 0 {name=l11 lab=GND}
C {devices/vsource.sym} -690 310 0 0 {name=V9 value="PULSE(0 1.8 0 100p 100p 484.8n 7756.8n)" savecurrent=false}
C {devices/lab_pin.sym} -690 280 2 0 {name=p35 lab=T0}
C {devices/gnd.sym} -690 340 0 0 {name=l12 lab=GND}
C {devices/vsource.sym} -690 400 0 0 {name=V10 value="PULSE(0 1.8 0 100p 100p 969.6n 7756.8n)" savecurrent=false}
C {devices/lab_pin.sym} -690 370 2 0 {name=p36 lab=T1}
C {devices/gnd.sym} -690 430 0 0 {name=l13 lab=GND}
C {devices/vsource.sym} -690 490 0 0 {name=V11 value="PULSE(0 1.8 0 100p 100p 1454.4n 7756.8n)" savecurrent=false}
C {devices/lab_pin.sym} -690 460 2 0 {name=p37 lab=T2}
C {devices/gnd.sym} -690 520 0 0 {name=l14 lab=GND}
C {devices/vsource.sym} -690 580 0 0 {name=V17 value="PULSE(0 1.8 0 100p 100p 1939.2n 7756.8n)" savecurrent=false}
C {devices/lab_pin.sym} -690 550 2 0 {name=p43 lab=T3}
C {devices/gnd.sym} -690 610 0 0 {name=l19 lab=GND}
C {devices/vsource.sym} -690 670 0 0 {name=V18 value="PULSE(0 1.8 0 100p 100p 2424n 7756.8n)" savecurrent=false}
C {devices/lab_pin.sym} -690 640 2 0 {name=p44 lab=T4}
C {devices/gnd.sym} -690 700 0 0 {name=l20 lab=GND}
C {devices/vsource.sym} -690 760 0 0 {name=V19 value="PULSE(0 1.8 0 100p 100p 2908.8n 7756.8n)" savecurrent=false}
C {devices/lab_pin.sym} -690 730 2 0 {name=p45 lab=T5}
C {devices/gnd.sym} -690 790 0 0 {name=l21 lab=GND}
C {devices/vsource.sym} -690 850 0 0 {name=V20 value="PULSE(0 1.8 0 100p 100p 3393.6n 7756.8n)" savecurrent=false}
C {devices/lab_pin.sym} -690 820 2 0 {name=p46 lab=T6}
C {devices/gnd.sym} -690 880 0 0 {name=l22 lab=GND}
C {devices/vsource.sym} -450 -140 0 0 {name=V12 value="PULSE(1.8 0 0 100p 100p 15.15n 30.3n)" savecurrent=false}
C {devices/lab_pin.sym} -450 -170 2 0 {name=p38 lab=B0_n}
C {devices/gnd.sym} -450 -110 0 0 {name=l15 lab=GND}
C {devices/vsource.sym} -450 -50 0 0 {name=V13 value="PULSE(1.8 0 0 100p 100p 30.3n 60.6n)" savecurrent=false}
C {devices/lab_pin.sym} -450 -80 2 0 {name=p39 lab=B1_n}
C {devices/gnd.sym} -450 -20 0 0 {name=l16 lab=GND}
C {devices/vsource.sym} -450 40 0 0 {name=V14 value="PULSE(1.8 0 0 100p 100p 60.6n 121.2n)" savecurrent=false}
C {devices/lab_pin.sym} -450 10 2 0 {name=p40 lab=B2_n}
C {devices/gnd.sym} -450 70 0 0 {name=l17 lab=GND}
C {devices/vsource.sym} -450 130 0 0 {name=V15 value="PULSE(1.8 0 0 100p 100p 121.2n 242.4n)" savecurrent=false}
C {devices/lab_pin.sym} -450 100 2 0 {name=p41 lab=B3_n}
C {devices/gnd.sym} -450 160 0 0 {name=l18 lab=GND}
C {devices/vsource.sym} -450 220 0 0 {name=V16 value="PULSE(1.8 0 0 100p 100p 242.4n 484.8n)" savecurrent=false}
C {devices/lab_pin.sym} -450 190 2 0 {name=p42 lab=B4_n}
C {devices/gnd.sym} -450 250 0 0 {name=l23 lab=GND}
C {devices/vsource.sym} -450 310 0 0 {name=V21 value="PULSE(1.8 0 0 100p 100p 484.8n 7756.8n)" savecurrent=false}
C {devices/lab_pin.sym} -450 280 2 0 {name=p47 lab=T0_n}
C {devices/gnd.sym} -450 340 0 0 {name=l24 lab=GND}
C {devices/vsource.sym} -450 400 0 0 {name=V22 value="PULSE(1.8 0 0 100p 100p 969.6n 7756.8n)" savecurrent=false}
C {devices/lab_pin.sym} -450 370 2 0 {name=p48 lab=T1_n}
C {devices/gnd.sym} -450 430 0 0 {name=l25 lab=GND}
C {devices/vsource.sym} -450 490 0 0 {name=V23 value="PULSE(1.8 0 0 100p 100p 1454.4n 7756.8n)" savecurrent=false}
C {devices/lab_pin.sym} -450 460 2 0 {name=p49 lab=T2_n}
C {devices/gnd.sym} -450 520 0 0 {name=l26 lab=GND}
C {devices/vsource.sym} -450 580 0 0 {name=V24 value="PULSE(1.8 0 0 100p 100p 1939.2n 7756.8n)" savecurrent=false}
C {devices/lab_pin.sym} -450 550 2 0 {name=p50 lab=T3_n}
C {devices/gnd.sym} -450 610 0 0 {name=l27 lab=GND}
C {devices/vsource.sym} -450 670 0 0 {name=V25 value="PULSE(1.8 0 0 100p 100p 2424n 7756.8n)" savecurrent=false}
C {devices/lab_pin.sym} -450 640 2 0 {name=p51 lab=T4_n}
C {devices/gnd.sym} -450 700 0 0 {name=l28 lab=GND}
C {devices/vsource.sym} -450 760 0 0 {name=V26 value="PULSE(1.8 0 0 100p 100p 2908.8n 7756.8n)" savecurrent=false}
C {devices/lab_pin.sym} -450 730 2 0 {name=p52 lab=T5_n}
C {devices/gnd.sym} -450 790 0 0 {name=l29 lab=GND}
C {devices/vsource.sym} -450 850 0 0 {name=V27 value="PULSE(1.8 0 0 100p 100p 3393.6n 7756.8n)" savecurrent=false}
C {devices/lab_pin.sym} -450 820 2 0 {name=p53 lab=T6_n}
C {devices/gnd.sym} -450 880 0 0 {name=l30 lab=GND}
C {sky130_fd_pr/corner.sym} 280 130 0 0 {name=CORNER only_toplevel=false corner=tt}
C {devices/lab_pin.sym} 320 -240 0 1 {name=p35 lab=I_main}
C {devices/gnd.sym} 320 -120 0 0 {name=l5 lab=GND}
C {devices/res.sym} 320 -150 0 0 {name=R5
value=1k
footprint=1206
device=resistor
m=1}
C {OpAmps/template/OpAmp.sym} 810 -190 0 0 {name=x2
spice_ignore=false}
C {devices/lab_pin.sym} 600 -240 2 1 {name=p44 lab=I_out_p
spice_ignore=false}
C {devices/gnd.sym} 790 -80 0 0 {name=l25 lab=GND
spice_ignore=false}
C {devices/vsource.sym} 730 -30 0 0 {name=V2 value=0.9 savecurrent=false
spice_ignore=false}
C {devices/gnd.sym} 730 0 0 0 {name=l26 lab=GND
spice_ignore=false}
C {devices/vsource.sym} 920 -320 0 0 {name=V3 value=1.8 savecurrent=false
spice_ignore=false}
C {devices/res.sym} 820 -410 1 0 {name=R4
value=1k
footprint=1206
device=resistor
m=1
spice_ignore=false}
C {devices/gnd.sym} 920 -290 0 0 {name=l28 lab=GND
spice_ignore=false}
C {devices/lab_pin.sym} 990 -190 0 1 {name=p45 lab=v_dac_out_p
spice_ignore=false}
C {devices/res.sym} 980 -160 2 0 {name=R1
value=1k
footprint=1206
device=resistor
m=1
spice_ignore=false}
C {devices/gnd.sym} 620 -100 0 0 {name=l6 lab=GND
spice_ignore=false}
C {devices/gnd.sym} 980 -130 0 0 {name=l11 lab=GND
spice_ignore=false}
C {OpAmps/template/OpAmp.sym} 810 290 0 0 {name=x3
spice_ignore=false}
C {devices/lab_pin.sym} 660 240 2 1 {name=p36 lab=I_out_n
spice_ignore=false}
C {devices/gnd.sym} 790 400 0 0 {name=l23 lab=GND
spice_ignore=false}
C {devices/gnd.sym} 730 480 0 0 {name=l24 lab=GND
spice_ignore=false}
C {devices/res.sym} 820 70 1 0 {name=R6
value=1k
footprint=1206
device=resistor
m=1
spice_ignore=false}
C {devices/gnd.sym} 920 190 0 0 {name=l30 lab=GND
spice_ignore=false}
C {devices/lab_pin.sym} 990 290 0 1 {name=p37 lab=v_dac_out_n
spice_ignore=false}
C {devices/gnd.sym} 620 380 0 0 {name=l31 lab=GND
spice_ignore=false}
C {devices/res.sym} 980 320 2 0 {name=R3
value=1k
footprint=1206
device=resistor
m=1
spice_ignore=false}
C {devices/gnd.sym} 980 350 0 0 {name=l12 lab=GND
spice_ignore=false}
C {devices/launcher.sym} 130 -500 0 0 {name=h5
descr="load waves" 
tclcommand="xschem raw_read $netlist_dir/seg_dac_tb.raw tran"
}
C {devices/lab_pin.sym} -70 300 0 0 {name=p29 lab=V_in}
C {devices/vsource.sym} -70 330 0 0 {name=V1 value=1.8 savecurrent=false}
C {devices/gnd.sym} -70 360 0 0 {name=l1 lab=GND}
C {devices/code_shown.sym} -20 460 0 0 {name=s1 only_toplevel=false value=".control
* Longer simulation with slower switching
tran 50p 3878.4n
* Plot differential output
let diff_out = v_dac_out_p - v_dac_out_n
plot diff_out

* Also plot individual outputs to see if one is noisier
plot v_dac_out_p v_dac_out_n

write seg_dac_tb.raw
.endc

.end"}
C {devices/vsource.sym} 320 -210 0 0 {name=V28 value=0 savecurrent=false}
C {devices/vsource.sym} 730 450 0 0 {name=V29 value=0.9 savecurrent=false
spice_ignore=false}
C {devices/vsource.sym} 920 160 0 0 {name=V30 value=1.8 savecurrent=false
spice_ignore=false}
C {devices/vsource.sym} 630 -240 3 0 {name=V31 value=0 savecurrent=false}
