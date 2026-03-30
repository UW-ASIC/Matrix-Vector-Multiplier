v {xschem version=3.4.7 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
B 2 -230 -190 570 210 {flags=graph
y1=-1.1e-05
y2=0.00026
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=3.876e-06
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
node=i(v31)
color=4
dataset=-1
unitx=1
logx=0
logy=0
}
N 760 650 820 650 {lab=#net1}
N 620 500 620 560 {lab=#net2}
N 620 500 770 500 {lab=#net2}
N 810 430 810 650 {lab=#net1}
N 710 430 810 430 {lab=#net1}
N 490 430 490 600 {lab=#net3}
N 490 430 650 430 {lab=#net3}
N 430 700 430 750 {lab=GND}
N 430 700 490 700 {lab=GND}
N 90 340 180 340 {lab=#net4}
N -940 -210 -940 150 {lab=B_n[4:0]
bus=true}
N -930 -220 -850 -220 {lab=B_n[0]}
N -930 140 -850 140 {lab=B_n[4]}
N -930 50 -850 50 {lab=B_n[3]}
N -930 -40 -850 -40 {lab=B_n[2]}
N -930 -130 -850 -130 {lab=B_n[1]}
N -930 230 -850 230 {lab=T_n[0]}
N -930 590 -850 590 {lab=T_n[4]}
N -930 500 -850 500 {lab=T_n[3]}
N -930 410 -850 410 {lab=T_n[2]}
N -930 320 -850 320 {lab=T_n[1]}
N -940 240 -940 780 {lab=T_n[6:0] bus=true}
N -930 680 -850 680 {lab=T_n[5]}
N -930 770 -850 770 {lab=T_n[6]}
N -640 230 -560 230 {lab=T[0]}
N -640 590 -560 590 {lab=T[4]}
N -640 500 -560 500 {lab=T[3]}
N -640 410 -560 410 {lab=T[2]}
N -640 320 -560 320 {lab=T[1]}
N -650 240 -650 780 {lab=T[6:0] bus=true}
N -640 680 -560 680 {lab=T[5]}
N -640 770 -560 770 {lab=T[6]}
N -650 -210 -650 150 {lab=B[4:0]
bus=true}
N -640 -220 -560 -220 {lab=B[0]}
N -640 140 -560 140 {lab=B[4]}
N -640 50 -560 50 {lab=B[3]}
N -640 -40 -560 -40 {lab=B[2]}
N -640 -130 -560 -130 {lab=B[1]}
C {devices/vsource.sym} -850 -190 0 0 {name=V4 value="PULSE(0 1.8 0 50p 50p 15.15n 30.3n)" savecurrent=false
spice_ignore=false}
C {devices/gnd.sym} -850 -160 0 0 {name=l7 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -850 -100 0 0 {name=V5 value="PULSE(0 1.8 0 50p 50p 30.3n 60.6n)" savecurrent=false
spice_ignore=false}
C {devices/gnd.sym} -850 -70 0 0 {name=l8 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -850 -10 0 0 {name=V6 value="PULSE(0 1.8 0 50p 50p 60.6n 121.2n)" savecurrent=false
spice_ignore=false}
C {devices/gnd.sym} -850 20 0 0 {name=l9 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -850 80 0 0 {name=V7 value="PULSE(0 1.8 0 50p 50p 121.2n 242.4n)" savecurrent=false
spice_ignore=false}
C {devices/gnd.sym} -850 110 0 0 {name=l10 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -850 170 0 0 {name=V8 value="PULSE(0 1.8 0 50p 50p 242.4n 484.8n)" savecurrent=false
spice_ignore=false}
C {devices/gnd.sym} -850 200 0 0 {name=l11 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -850 260 0 0 {name=V9 value="PULSE(0 1.8 0 50p 50p 484.8n 7756.8n)" savecurrent=false
spice_ignore=false}
C {devices/gnd.sym} -850 290 0 0 {name=l12 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -850 350 0 0 {name=V10 value="PULSE(0 1.8 0 50p 50p 969.6n 7756.8n)" savecurrent=false
spice_ignore=false}
C {devices/gnd.sym} -850 380 0 0 {name=l13 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -850 440 0 0 {name=V11 value="PULSE(0 1.8 0 50p 50p 1454.4n 7756.8n)" savecurrent=false
spice_ignore=false}
C {devices/gnd.sym} -850 470 0 0 {name=l14 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -850 530 0 0 {name=V17 value="PULSE(0 1.8 0 50p 50p 1939.2n 7756.8n)" savecurrent=false
spice_ignore=false}
C {devices/gnd.sym} -850 560 0 0 {name=l19 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -850 620 0 0 {name=V18 value="PULSE(0 1.8 0 50p 50p 2424n 7756.8n)" savecurrent=false
spice_ignore=false}
C {devices/gnd.sym} -850 650 0 0 {name=l20 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -850 710 0 0 {name=V19 value="PULSE(0 1.8 0 50p 50p 2908.8n 7756.8n)" savecurrent=false
spice_ignore=false}
C {devices/gnd.sym} -850 740 0 0 {name=l21 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -850 800 0 0 {name=V20 value="PULSE(0 1.8 0 50p 50p 3393.6n 7756.8n)" savecurrent=false
spice_ignore=false}
C {devices/gnd.sym} -850 830 0 0 {name=l22 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -560 -190 0 0 {name=V12 value="PULSE(1.8 0 0 50p 50p 15.15n 30.3n)" savecurrent=false
spice_ignore=false}
C {devices/gnd.sym} -560 -160 0 0 {name=l15 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -560 -100 0 0 {name=V13 value="PULSE(1.8 0 0 50p 50p 30.3n 60.6n)" savecurrent=false
spice_ignore=false}
C {devices/gnd.sym} -560 -70 0 0 {name=l16 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -560 -10 0 0 {name=V14 value="PULSE(1.8 0 0 50p 50p 60.6n 121.2n)" savecurrent=false
spice_ignore=false}
C {devices/gnd.sym} -560 20 0 0 {name=l17 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -560 80 0 0 {name=V15 value="PULSE(1.8 0 0 50p 50p 121.2n 242.4n)" savecurrent=false
spice_ignore=false}
C {devices/gnd.sym} -560 110 0 0 {name=l18 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -560 170 0 0 {name=V16 value="PULSE(1.8 0 0 50p 50p 242.4n 484.8n)" savecurrent=false
spice_ignore=false}
C {devices/gnd.sym} -560 200 0 0 {name=l23 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -560 260 0 0 {name=V21 value="PULSE(1.8 0 0 50p 50p 484.8n 7756.8n)" savecurrent=false
spice_ignore=false}
C {devices/gnd.sym} -560 290 0 0 {name=l24 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -560 350 0 0 {name=V22 value="PULSE(1.8 0 0 50p 50p 969.6n 7756.8n)" savecurrent=false
spice_ignore=false}
C {devices/gnd.sym} -560 380 0 0 {name=l25 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -560 440 0 0 {name=V23 value="PULSE(1.8 0 0 50p 50p 1454.4n 7756.8n)" savecurrent=false
spice_ignore=false}
C {devices/gnd.sym} -560 470 0 0 {name=l26 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -560 530 0 0 {name=V24 value="PULSE(1.8 0 0 50p 50p 1939.2n 7756.8n)" savecurrent=false
spice_ignore=false}
C {devices/gnd.sym} -560 560 0 0 {name=l27 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -560 620 0 0 {name=V25 value="PULSE(1.8 0 0 50p 50p 2424n 7756.8n)" savecurrent=false
spice_ignore=false}
C {devices/gnd.sym} -560 650 0 0 {name=l28 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -560 710 0 0 {name=V26 value="PULSE(1.8 0 0 50p 50p 2908.8n 7756.8n)" savecurrent=false
spice_ignore=false}
C {devices/gnd.sym} -560 740 0 0 {name=l29 lab=GND
spice_ignore=false}
C {devices/vsource.sym} -560 800 0 0 {name=V27 value="PULSE(1.8 0 0 50p 50p 3393.6n 7756.8n)" savecurrent=false
spice_ignore=false}
C {devices/gnd.sym} -560 830 0 0 {name=l30 lab=GND
spice_ignore=false}
C {sky130_fd_pr/corner.sym} 200 720 0 0 {name=CORNER only_toplevel=false corner=tt}
C {devices/lab_pin.sym} 430 600 2 1 {name=p44 lab=I_out_p
spice_ignore=false}
C {devices/vsource.sym} 770 530 0 0 {name=V3 value=1.8 savecurrent=false
spice_ignore=false}
C {devices/gnd.sym} 770 560 0 0 {name=l28 lab=GND
spice_ignore=false}
C {devices/lab_pin.sym} 880 650 0 1 {name=p45 lab=v_dac_out
spice_ignore=false}
C {devices/res.sym} 810 680 2 0 {name=R1
value=1k
footprint=1206
device=resistor
m=1
spice_ignore=false}
C {devices/gnd.sym} 810 710 0 0 {name=l11 lab=GND
spice_ignore=false}
C {devices/lab_pin.sym} 140 700 0 0 {name=p29 lab=V_in}
C {devices/vsource.sym} 140 730 0 0 {name=V1 value=1.8 savecurrent=false}
C {devices/gnd.sym} 140 820 0 0 {name=l1 lab=GND}
C {devices/code_shown.sym} 460 260 0 0 {name=s1 only_toplevel=false value=".control
  options savecurrents
  tran 1n 3876n
  let power=(abs(v_in*v32#branch))
  write seg_dac_tb.raw
.endc
.end"}
C {devices/vsource.sym} 460 600 3 0 {name=V31 value=0 savecurrent=false}
C {OpAmp/Two-Stage_Miller/OpAmp.sym} 640 650 0 0 {name=x2}
C {devices/res.sym} 680 430 3 0 {name=R3
value=1k
footprint=1206
device=resistor
m=1
spice_ignore=false}
C {devices/gnd.sym} 430 750 0 0 {name=l3 lab=GND}
C {devices/vsource.sym} 560 810 0 0 {name=V2 value=0.9 savecurrent=false}
C {devices/gnd.sym} 560 840 0 0 {name=l4 lab=GND}
C {devices/gnd.sym} 620 740 0 0 {name=l6 lab=GND}
C {devices/res.sym} 850 650 3 0 {name=R4
value=200
footprint=1206
device=resistor
m=1
spice_ignore=false}
C {devices/capa.sym} 880 680 2 0 {name=C1
m=1
value=1p
footprint=1206
device="ceramic capacitor"}
C {devices/gnd.sym} 880 710 0 0 {name=l31 lab=GND
spice_ignore=false}
C {devices/launcher.sym} -160 260 0 0 {name=h5
descr="load waves" 
tclcommand="xschem raw_read $netlist_dir/seg_dac_tb.raw tran"
}
C {devices/lab_pin.sym} -210 340 0 0 {name=p1 lab=V_in}
C {devices/lab_pin.sym} -210 360 0 0 {name=p2 lab=I_ref}
C {devices/lab_pin.sym} 90 360 0 1 {name=p4 lab=I_out_p}
C {devices/lab_pin.sym} 250 510 0 0 {name=p3 lab=I_ref}
C {devices/isource.sym} 250 540 0 0 {name=I0 value=8u}
C {devices/vsource.sym} 140 790 0 0 {name=V32 value=0 savecurrent=false}
C {devices/gnd.sym} 180 400 0 0 {name=l2 lab=GND}
C {devices/vsource.sym} 180 370 0 0 {name=V33 value=0 savecurrent=false}
C {components/DAC/segmented_dac.sym} -60 390 0 0 {name=x1}
C {devices/code_shown.sym} 830 280 0 0 {name=s2 only_toplevel=false value=".param min_width=0.42
.param switch_multiplier=1
.param length=0.425
.param switch_length=0.15
.param size_multiplier=5"
W=min_width
L=length}
C {devices/gnd.sym} 250 570 0 0 {name=l5 lab=GND}
C {devices/lab_pin.sym} -210 380 0 0 {name=p5 lab=B[4:0]}
C {devices/bus_tap.sym} -940 150 0 0 {name=l33 lab=[4]}
C {devices/bus_tap.sym} -940 -210 0 0 {name=l35 lab=[0]}
C {devices/bus_tap.sym} -940 60 0 0 {name=l36 lab=[3]}
C {devices/bus_tap.sym} -940 -30 0 0 {name=l37 lab=[2]}
C {devices/bus_tap.sym} -940 -120 0 0 {name=l38 lab=[1]}
C {devices/bus_tap.sym} -940 600 0 0 {name=l34 lab=[4]}
C {devices/bus_tap.sym} -940 240 0 0 {name=l39 lab=[0]}
C {devices/bus_tap.sym} -940 510 0 0 {name=l40 lab=[3]}
C {devices/bus_tap.sym} -940 420 0 0 {name=l41 lab=[2]}
C {devices/bus_tap.sym} -940 330 0 0 {name=l42 lab=[1]}
C {devices/bus_tap.sym} -940 690 0 0 {name=l43 lab=[5]}
C {devices/bus_tap.sym} -940 780 0 0 {name=l44 lab=[6]}
C {devices/bus_tap.sym} -650 600 0 0 {name=l45 lab=[4]}
C {devices/bus_tap.sym} -650 240 0 0 {name=l46 lab=[0]}
C {devices/bus_tap.sym} -650 510 0 0 {name=l47 lab=[3]}
C {devices/bus_tap.sym} -650 420 0 0 {name=l48 lab=[2]}
C {devices/bus_tap.sym} -650 330 0 0 {name=l49 lab=[1]}
C {devices/bus_tap.sym} -650 690 0 0 {name=l50 lab=[5]}
C {devices/bus_tap.sym} -650 780 0 0 {name=l51 lab=[6]}
C {devices/bus_tap.sym} -650 150 0 0 {name=l52 lab=[4]}
C {devices/bus_tap.sym} -650 -210 0 0 {name=l53 lab=[0]}
C {devices/bus_tap.sym} -650 60 0 0 {name=l54 lab=[3]}
C {devices/bus_tap.sym} -650 -30 0 0 {name=l55 lab=[2]}
C {devices/bus_tap.sym} -650 -120 0 0 {name=l56 lab=[1]}
C {devices/lab_pin.sym} -650 -210 0 0 {name=p9 lab=B[4:0]}
C {devices/lab_pin.sym} -210 400 0 0 {name=p6 lab=T[6:0]}
C {devices/lab_pin.sym} -210 420 0 0 {name=p7 lab=T_n[6:0]}
C {devices/lab_pin.sym} -210 440 0 0 {name=p8 lab=B_n[4:0]}
C {devices/lab_pin.sym} -940 240 0 0 {name=p10 lab=T_n[6:0]}
C {devices/lab_pin.sym} -940 -210 0 0 {name=p11 lab=B_n[4:0]}
C {devices/lab_pin.sym} -650 240 0 0 {name=p12 lab=T[6:0]}
