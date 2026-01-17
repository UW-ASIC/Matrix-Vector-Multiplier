v {xschem version=3.4.7 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
B 2 -850 -690 -50 -290 {flags=graph
y1=-8.2e-05
y2=0.075
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=1.7598902e-06
x2=3.1476313e-06
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
node="v_dac_out_p
i(v31)"
color="4 12"
dataset=5
unitx=1
logx=0
logy=0
}
N 930 -190 990 -190 {lab=#net1}
N 790 -340 790 -280 {lab=#net2}
N 790 -340 940 -340 {lab=#net2}
N 980 -410 980 -190 {lab=#net1}
N 880 -410 980 -410 {lab=#net1}
N 660 -410 660 -240 {lab=#net3}
N 660 -410 820 -410 {lab=#net3}
N 600 -140 600 -90 {lab=GND}
N 600 -140 660 -140 {lab=GND}
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
C {devices/vsource.sym} -800 -190 0 0 {name=V4 value="PULSE(0 1.8 0 50p 50p 15.15n 30.3n)" savecurrent=false
spice_ignore=false}
C {devices/lab_pin.sym} -800 -220 2 0 {name=p30 lab=B0
spice_ignore=false}
C {devices/gnd.sym} -800 -160 0 0 {name=l7 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -800 -100 0 0 {name=V5 value="PULSE(0 1.8 0 50p 50p 30.3n 60.6n)" savecurrent=false
spice_ignore=false}
C {devices/lab_pin.sym} -800 -130 2 0 {name=p31 lab=B1
spice_ignore=false}
C {devices/gnd.sym} -800 -70 0 0 {name=l8 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -800 -10 0 0 {name=V6 value="PULSE(0 1.8 0 50p 50p 60.6n 121.2n)" savecurrent=false
spice_ignore=false}
C {devices/lab_pin.sym} -800 -40 2 0 {name=p32 lab=B2
spice_ignore=false}
C {devices/gnd.sym} -800 20 0 0 {name=l9 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -800 80 0 0 {name=V7 value="PULSE(0 1.8 0 50p 50p 121.2n 242.4n)" savecurrent=false
spice_ignore=false}
C {devices/lab_pin.sym} -800 50 2 0 {name=p33 lab=B3
spice_ignore=false}
C {devices/gnd.sym} -800 110 0 0 {name=l10 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -800 170 0 0 {name=V8 value="PULSE(0 1.8 0 50p 50p 242.4n 484.8n)" savecurrent=false
spice_ignore=false}
C {devices/lab_pin.sym} -800 140 2 0 {name=p34 lab=B4
spice_ignore=false}
C {devices/gnd.sym} -800 200 0 0 {name=l11 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -800 260 0 0 {name=V9 value="PULSE(0 1.8 0 50p 50p 484.8n 7756.8n)" savecurrent=false
spice_ignore=false}
C {devices/lab_pin.sym} -800 230 2 0 {name=p35 lab=T0
spice_ignore=false}
C {devices/gnd.sym} -800 290 0 0 {name=l12 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -800 350 0 0 {name=V10 value="PULSE(0 1.8 0 50p 50p 969.6n 7756.8n)" savecurrent=false
spice_ignore=false}
C {devices/lab_pin.sym} -800 320 2 0 {name=p36 lab=T1
spice_ignore=false}
C {devices/gnd.sym} -800 380 0 0 {name=l13 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -800 440 0 0 {name=V11 value="PULSE(0 1.8 0 50p 50p 1454.4n 7756.8n)" savecurrent=false
spice_ignore=false}
C {devices/lab_pin.sym} -800 410 2 0 {name=p37 lab=T2
spice_ignore=false}
C {devices/gnd.sym} -800 470 0 0 {name=l14 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -800 530 0 0 {name=V17 value="PULSE(0 1.8 0 50p 50p 1939.2n 7756.8n)" savecurrent=false
spice_ignore=false}
C {devices/lab_pin.sym} -800 500 2 0 {name=p43 lab=T3
spice_ignore=false}
C {devices/gnd.sym} -800 560 0 0 {name=l19 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -800 620 0 0 {name=V18 value="PULSE(0 1.8 0 50p 50p 2424n 7756.8n)" savecurrent=false
spice_ignore=false}
C {devices/lab_pin.sym} -800 590 2 0 {name=p44 lab=T4
spice_ignore=false}
C {devices/gnd.sym} -800 650 0 0 {name=l20 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -800 710 0 0 {name=V19 value="PULSE(0 1.8 0 50p 50p 2908.8n 7756.8n)" savecurrent=false
spice_ignore=false}
C {devices/lab_pin.sym} -800 680 2 0 {name=p45 lab=T5
spice_ignore=false}
C {devices/gnd.sym} -800 740 0 0 {name=l21 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -800 800 0 0 {name=V20 value="PULSE(0 1.8 0 50p 50p 3393.6n 7756.8n)" savecurrent=false
spice_ignore=false}
C {devices/lab_pin.sym} -800 770 2 0 {name=p46 lab=T6
spice_ignore=false}
C {devices/gnd.sym} -800 830 0 0 {name=l22 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -560 -190 0 0 {name=V12 value="PULSE(1.8 0 0 50p 50p 15.15n 30.3n)" savecurrent=false
spice_ignore=false}
C {devices/lab_pin.sym} -560 -220 2 0 {name=p38 lab=B0_n
spice_ignore=false}
C {devices/gnd.sym} -560 -160 0 0 {name=l15 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -560 -100 0 0 {name=V13 value="PULSE(1.8 0 0 50p 50p 30.3n 60.6n)" savecurrent=false
spice_ignore=false}
C {devices/lab_pin.sym} -560 -130 2 0 {name=p39 lab=B1_n
spice_ignore=false}
C {devices/gnd.sym} -560 -70 0 0 {name=l16 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -560 -10 0 0 {name=V14 value="PULSE(1.8 0 0 50p 50p 60.6n 121.2n)" savecurrent=false
spice_ignore=false}
C {devices/lab_pin.sym} -560 -40 2 0 {name=p40 lab=B2_n
spice_ignore=false}
C {devices/gnd.sym} -560 20 0 0 {name=l17 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -560 80 0 0 {name=V15 value="PULSE(1.8 0 0 50p 50p 121.2n 242.4n)" savecurrent=false
spice_ignore=false}
C {devices/lab_pin.sym} -560 50 2 0 {name=p41 lab=B3_n
spice_ignore=false}
C {devices/gnd.sym} -560 110 0 0 {name=l18 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -560 170 0 0 {name=V16 value="PULSE(1.8 0 0 50p 50p 242.4n 484.8n)" savecurrent=false
spice_ignore=false}
C {devices/lab_pin.sym} -560 140 2 0 {name=p42 lab=B4_n
spice_ignore=false}
C {devices/gnd.sym} -560 200 0 0 {name=l23 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -560 260 0 0 {name=V21 value="PULSE(1.8 0 0 50p 50p 484.8n 7756.8n)" savecurrent=false
spice_ignore=false}
C {devices/lab_pin.sym} -560 230 2 0 {name=p47 lab=T0_n
spice_ignore=false}
C {devices/gnd.sym} -560 290 0 0 {name=l24 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -560 350 0 0 {name=V22 value="PULSE(1.8 0 0 50p 50p 969.6n 7756.8n)" savecurrent=false
spice_ignore=false}
C {devices/lab_pin.sym} -560 320 2 0 {name=p48 lab=T1_n
spice_ignore=false}
C {devices/gnd.sym} -560 380 0 0 {name=l25 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -560 440 0 0 {name=V23 value="PULSE(1.8 0 0 50p 50p 1454.4n 7756.8n)" savecurrent=false
spice_ignore=false}
C {devices/lab_pin.sym} -560 410 2 0 {name=p49 lab=T2_n
spice_ignore=false}
C {devices/gnd.sym} -560 470 0 0 {name=l26 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -560 530 0 0 {name=V24 value="PULSE(1.8 0 0 50p 50p 1939.2n 7756.8n)" savecurrent=false
spice_ignore=false}
C {devices/lab_pin.sym} -560 500 2 0 {name=p50 lab=T3_n
spice_ignore=false}
C {devices/gnd.sym} -560 560 0 0 {name=l27 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -560 620 0 0 {name=V25 value="PULSE(1.8 0 0 50p 50p 2424n 7756.8n)" savecurrent=false
spice_ignore=false}
C {devices/lab_pin.sym} -560 590 2 0 {name=p51 lab=T4_n
spice_ignore=false}
C {devices/gnd.sym} -560 650 0 0 {name=l28 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -560 710 0 0 {name=V26 value="PULSE(1.8 0 0 50p 50p 2908.8n 7756.8n)" savecurrent=false
spice_ignore=false}
C {devices/lab_pin.sym} -560 680 2 0 {name=p52 lab=T5_n
spice_ignore=false}
C {devices/gnd.sym} -560 740 0 0 {name=l29 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -560 800 0 0 {name=V27 value="PULSE(1.8 0 0 50p 50p 3393.6n 7756.8n)" savecurrent=false
spice_ignore=false}
C {devices/lab_pin.sym} -560 770 2 0 {name=p53 lab=T6_n
spice_ignore=false}
C {devices/gnd.sym} -560 830 0 0 {name=l30 lab=GND
spice_ignore=false}
C {sky130_fd_pr/corner.sym} 280 130 0 0 {name=CORNER only_toplevel=false corner=tt_mm}
C {devices/lab_pin.sym} 320 -240 0 1 {name=p35 lab=I_main}
C {devices/gnd.sym} 320 -120 0 0 {name=l5 lab=GND}
C {devices/res.sym} 320 -150 0 0 {name=R5
value=1k
footprint=1206
device=resistor
m=1}
C {devices/lab_pin.sym} 600 -240 2 1 {name=p44 lab=I_out_p
spice_ignore=false}
C {devices/vsource.sym} 940 -310 0 0 {name=V3 value=1.8 savecurrent=false
spice_ignore=false}
C {devices/gnd.sym} 940 -280 0 0 {name=l28 lab=GND
spice_ignore=false}
C {devices/lab_pin.sym} 1050 -190 0 1 {name=p45 lab=v_dac_out_p
spice_ignore=false}
C {devices/res.sym} 980 -160 2 0 {name=R1
value=1k
footprint=1206
device=resistor
m=1
spice_ignore=false}
C {devices/gnd.sym} 980 -130 0 0 {name=l11 lab=GND
spice_ignore=false}
C {devices/launcher.sym} 130 -500 0 0 {name=h5
descr="load waves" 
tclcommand="xschem raw_read $netlist_dir/seg_dac_tb.raw tran"
}
C {devices/lab_pin.sym} -70 300 0 0 {name=p29 lab=V_in}
C {devices/vsource.sym} -70 330 0 0 {name=V1 value=1.8 savecurrent=false}
C {devices/gnd.sym} -70 360 0 0 {name=l1 lab=GND}
C {devices/code_shown.sym} -20 460 0 0 {name=s1 only_toplevel=false value=".control
let run=0
dowhile run <= 100
  save all
  tran 1n 4u
  remzerovec
  write seg_dac_tb.raw
  set appendwrite
  reset 
  let run=run+=1
end
.endc
.end"}
C {devices/vsource.sym} 320 -210 0 0 {name=V28 value=0 savecurrent=false}
C {devices/vsource.sym} 630 -240 3 0 {name=V31 value=0 savecurrent=false}
C {devices/res.sym} 550 10 2 0 {name=R2
value=1k
footprint=1206
device=resistor
m=1
spice_ignore=false}
C {devices/lab_pin.sym} 550 -20 0 1 {name=p54 lab=I_out_n}
C {devices/gnd.sym} 550 40 0 0 {name=l2 lab=GND}
C {OpAmp/Two-Stage_Miller/OpAmp.sym} 810 -190 0 0 {name=x2}
C {devices/res.sym} 850 -410 3 0 {name=R3
value=1k
footprint=1206
device=resistor
m=1
spice_ignore=false}
C {devices/gnd.sym} 600 -90 0 0 {name=l3 lab=GND}
C {devices/vsource.sym} 730 -30 0 0 {name=V2 value=0.9 savecurrent=false}
C {devices/gnd.sym} 730 0 0 0 {name=l4 lab=GND}
C {devices/gnd.sym} 790 -100 0 0 {name=l6 lab=GND}
C {devices/res.sym} 1020 -190 3 0 {name=R4
value=500
footprint=1206
device=resistor
m=1
spice_ignore=false}
C {devices/capa.sym} 1050 -160 2 0 {name=C1
m=1
value=500f
footprint=1206
device="ceramic capacitor"}
C {devices/gnd.sym} 1050 -130 0 0 {name=l31 lab=GND
spice_ignore=false}
