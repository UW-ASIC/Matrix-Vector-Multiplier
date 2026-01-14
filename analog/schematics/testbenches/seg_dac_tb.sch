v {xschem version=3.4.7 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
B 2 -850 -690 -50 -290 {flags=graph
y1=-0.014924455
y2=0.06699757
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=-6.0143125e-07
x2=7.2589465e-06
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
N 930 -190 990 -190 {lab=v_dac_out_p}
N 790 -340 790 -280 {lab=#net1}
N 790 -340 940 -340 {lab=#net1}
N 980 -410 980 -190 {lab=v_dac_out_p}
N 880 -410 980 -410 {lab=v_dac_out_p}
N 660 -410 660 -240 {lab=#net2}
N 660 -410 820 -410 {lab=#net2}
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
C {devices/vsource.sym} -1570 -160 0 0 {name=V4 value="PULSE(0 1.8 0 1n 1n 15.15n 30.3n)" savecurrent=false
spice_ignore=true}
C {devices/lab_pin.sym} -1570 -190 2 0 {name=p30 lab=B0
spice_ignore=true}
C {devices/gnd.sym} -1570 -130 0 0 {name=l7 lab=GND
spice_ignore=true}
C {devices/vsource.sym} -1570 -70 0 0 {name=V5 value="PULSE(0 1.8 0 1n 1n 30.3n 60.6n)" savecurrent=false
spice_ignore=true}
C {devices/lab_pin.sym} -1570 -100 2 0 {name=p31 lab=B1
spice_ignore=true}
C {devices/gnd.sym} -1570 -40 0 0 {name=l8 lab=GND
spice_ignore=true}
C {devices/vsource.sym} -1570 20 0 0 {name=V6 value="PULSE(0 1.8 0 1n 1n 60.6n 121.2n)" savecurrent=false
spice_ignore=true}
C {devices/lab_pin.sym} -1570 -10 2 0 {name=p32 lab=B2
spice_ignore=true}
C {devices/gnd.sym} -1570 50 0 0 {name=l9 lab=GND
spice_ignore=true}
C {devices/vsource.sym} -1570 110 0 0 {name=V7 value="PULSE(0 1.8 0 1n 1n 121.2n 242.4n)" savecurrent=false
spice_ignore=true}
C {devices/lab_pin.sym} -1570 80 2 0 {name=p33 lab=B3
spice_ignore=true}
C {devices/gnd.sym} -1570 140 0 0 {name=l10 lab=GND
spice_ignore=true}
C {devices/vsource.sym} -1570 200 0 0 {name=V8 value="PULSE(0 1.8 0 1n 1n 242.4n 484.8n)" savecurrent=false
spice_ignore=true}
C {devices/lab_pin.sym} -1570 170 2 0 {name=p34 lab=B4
spice_ignore=true}
C {devices/gnd.sym} -1570 230 0 0 {name=l11 lab=GND
spice_ignore=true}
C {devices/vsource.sym} -1570 290 0 0 {name=V9 value="PULSE(0 1.8 0 1n 1n 484.8n 7756.8n)" savecurrent=false
spice_ignore=true}
C {devices/lab_pin.sym} -1570 260 2 0 {name=p35 lab=T0
spice_ignore=true}
C {devices/gnd.sym} -1570 320 0 0 {name=l12 lab=GND
spice_ignore=true}
C {devices/vsource.sym} -1570 380 0 0 {name=V10 value="PULSE(0 1.8 0 1n 1n 969.6n 7756.8n)" savecurrent=false
spice_ignore=true}
C {devices/lab_pin.sym} -1570 350 2 0 {name=p36 lab=T1
spice_ignore=true}
C {devices/gnd.sym} -1570 410 0 0 {name=l13 lab=GND
spice_ignore=true}
C {devices/vsource.sym} -1570 470 0 0 {name=V11 value="PULSE(0 1.8 0 1n 1n 1454.4n 7756.8n)" savecurrent=false
spice_ignore=true}
C {devices/lab_pin.sym} -1570 440 2 0 {name=p37 lab=T2
spice_ignore=true}
C {devices/gnd.sym} -1570 500 0 0 {name=l14 lab=GND
spice_ignore=true}
C {devices/vsource.sym} -1570 560 0 0 {name=V17 value="PULSE(0 1.8 0 1n 1n 1939.2n 7756.8n)" savecurrent=false
spice_ignore=true}
C {devices/lab_pin.sym} -1570 530 2 0 {name=p43 lab=T3
spice_ignore=true}
C {devices/gnd.sym} -1570 590 0 0 {name=l19 lab=GND
spice_ignore=true}
C {devices/vsource.sym} -1570 650 0 0 {name=V18 value="PULSE(0 1.8 0 1n 1n 2424n 7756.8n)" savecurrent=false
spice_ignore=true}
C {devices/lab_pin.sym} -1570 620 2 0 {name=p44 lab=T4
spice_ignore=true}
C {devices/gnd.sym} -1570 680 0 0 {name=l20 lab=GND
spice_ignore=true}
C {devices/vsource.sym} -1570 740 0 0 {name=V19 value="PULSE(0 1.8 0 1n 1n 2908.8n 7756.8n)" savecurrent=false
spice_ignore=true}
C {devices/lab_pin.sym} -1570 710 2 0 {name=p45 lab=T5
spice_ignore=true}
C {devices/gnd.sym} -1570 770 0 0 {name=l21 lab=GND
spice_ignore=true}
C {devices/vsource.sym} -1570 830 0 0 {name=V20 value="PULSE(0 1.8 0 1n 1n 3393.6n 7756.8n)" savecurrent=false
spice_ignore=true}
C {devices/lab_pin.sym} -1570 800 2 0 {name=p46 lab=T6
spice_ignore=true}
C {devices/gnd.sym} -1570 860 0 0 {name=l22 lab=GND
spice_ignore=true}
C {devices/vsource.sym} -1330 -160 0 0 {name=V12 value="PULSE(1.8 0 0 1n 1n 15.15n 30.3n)" savecurrent=false
spice_ignore=true}
C {devices/lab_pin.sym} -1330 -190 2 0 {name=p38 lab=B0_n
spice_ignore=true}
C {devices/gnd.sym} -1330 -130 0 0 {name=l15 lab=GND
spice_ignore=true}
C {devices/vsource.sym} -1330 -70 0 0 {name=V13 value="PULSE(1.8 0 0 1n 1n 30.3n 60.6n)" savecurrent=false
spice_ignore=true}
C {devices/lab_pin.sym} -1330 -100 2 0 {name=p39 lab=B1_n
spice_ignore=true}
C {devices/gnd.sym} -1330 -40 0 0 {name=l16 lab=GND
spice_ignore=true}
C {devices/vsource.sym} -1330 20 0 0 {name=V14 value="PULSE(1.8 0 0 1n 1n 60.6n 121.2n)" savecurrent=false
spice_ignore=true}
C {devices/lab_pin.sym} -1330 -10 2 0 {name=p40 lab=B2_n
spice_ignore=true}
C {devices/gnd.sym} -1330 50 0 0 {name=l17 lab=GND
spice_ignore=true}
C {devices/vsource.sym} -1330 110 0 0 {name=V15 value="PULSE(1.8 0 0 1n 1n 121.2n 242.4n)" savecurrent=false
spice_ignore=true}
C {devices/lab_pin.sym} -1330 80 2 0 {name=p41 lab=B3_n
spice_ignore=true}
C {devices/gnd.sym} -1330 140 0 0 {name=l18 lab=GND
spice_ignore=true}
C {devices/vsource.sym} -1330 200 0 0 {name=V16 value="PULSE(1.8 0 0 1n 1n 242.4n 484.8n)" savecurrent=false
spice_ignore=true}
C {devices/lab_pin.sym} -1330 170 2 0 {name=p42 lab=B4_n
spice_ignore=true}
C {devices/gnd.sym} -1330 230 0 0 {name=l23 lab=GND
spice_ignore=true}
C {devices/vsource.sym} -1330 290 0 0 {name=V21 value="PULSE(1.8 0 0 1n 1n 484.8n 7756.8n)" savecurrent=false
spice_ignore=true}
C {devices/lab_pin.sym} -1330 260 2 0 {name=p47 lab=T0_n
spice_ignore=true}
C {devices/gnd.sym} -1330 320 0 0 {name=l24 lab=GND
spice_ignore=true}
C {devices/vsource.sym} -1330 380 0 0 {name=V22 value="PULSE(1.8 0 0 1n 1n 969.6n 7756.8n)" savecurrent=false
spice_ignore=true}
C {devices/lab_pin.sym} -1330 350 2 0 {name=p48 lab=T1_n
spice_ignore=true}
C {devices/gnd.sym} -1330 410 0 0 {name=l25 lab=GND
spice_ignore=true}
C {devices/vsource.sym} -1330 470 0 0 {name=V23 value="PULSE(1.8 0 0 1n 1n 1454.4n 7756.8n)" savecurrent=false
spice_ignore=true}
C {devices/lab_pin.sym} -1330 440 2 0 {name=p49 lab=T2_n
spice_ignore=true}
C {devices/gnd.sym} -1330 500 0 0 {name=l26 lab=GND
spice_ignore=true}
C {devices/vsource.sym} -1330 560 0 0 {name=V24 value="PULSE(1.8 0 0 1n 1n 1939.2n 7756.8n)" savecurrent=false
spice_ignore=true}
C {devices/lab_pin.sym} -1330 530 2 0 {name=p50 lab=T3_n
spice_ignore=true}
C {devices/gnd.sym} -1330 590 0 0 {name=l27 lab=GND
spice_ignore=true}
C {devices/vsource.sym} -1330 650 0 0 {name=V25 value="PULSE(1.8 0 0 1n 1n 2424n 7756.8n)" savecurrent=false
spice_ignore=true}
C {devices/lab_pin.sym} -1330 620 2 0 {name=p51 lab=T4_n
spice_ignore=true}
C {devices/gnd.sym} -1330 680 0 0 {name=l28 lab=GND
spice_ignore=true}
C {devices/vsource.sym} -1330 740 0 0 {name=V26 value="PULSE(1.8 0 0 1n 1n 2908.8n 7756.8n)" savecurrent=false
spice_ignore=true}
C {devices/lab_pin.sym} -1330 710 2 0 {name=p52 lab=T5_n
spice_ignore=true}
C {devices/gnd.sym} -1330 770 0 0 {name=l29 lab=GND
spice_ignore=true}
C {devices/vsource.sym} -1330 830 0 0 {name=V27 value="PULSE(1.8 0 0 1n 1n 3393.6n 7756.8n)" savecurrent=false
spice_ignore=true}
C {devices/lab_pin.sym} -1330 800 2 0 {name=p53 lab=T6_n
spice_ignore=true}
C {devices/gnd.sym} -1330 860 0 0 {name=l30 lab=GND
spice_ignore=true}
C {sky130_fd_pr/corner.sym} 280 130 0 0 {name=CORNER only_toplevel=false corner=tt}
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
C {devices/lab_pin.sym} 990 -190 0 1 {name=p45 lab=v_dac_out_p
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
C {devices/vsource.sym} -770 -180 0 0 {name=V29 value="PWL FILE \\"bit_b0.pwl\\"" savecurrent=false}
C {devices/lab_pin.sym} -770 -210 2 0 {name=p55 lab=B0
value="PWL FILE \\"bit_b0.pwl\\""}
C {devices/gnd.sym} -770 -150 0 0 {name=l32 lab=GND
value="PWL FILE \\"bit_b0.pwl\\""}
C {devices/vsource.sym} -770 -90 0 0 {name=V30 value="PWL FILE \\"bit_b1.pwl\\"" savecurrent=false}
C {devices/lab_pin.sym} -770 -120 2 0 {name=p56 lab=B1
value="PWL FILE \\"bit_b1.pwl\\""}
C {devices/gnd.sym} -770 -60 0 0 {name=l33 lab=GND
value="PWL FILE \\"bit_b1.pwl\\""}
C {devices/vsource.sym} -770 0 0 0 {name=V32 value="PWL FILE \\"bit_b2.pwl\\"" savecurrent=false}
C {devices/lab_pin.sym} -770 -30 2 0 {name=p57 lab=B2
value="PWL FILE \\"bit_b2.pwl\\""}
C {devices/gnd.sym} -770 30 0 0 {name=l34 lab=GND
value="PWL FILE \\"bit_b2.pwl\\""}
C {devices/vsource.sym} -770 90 0 0 {name=V33 value="PWL FILE \\"bit_b3.pwl\\"" savecurrent=false}
C {devices/lab_pin.sym} -770 60 2 0 {name=p58 lab=B3
value="PWL FILE \\"bit_b3.pwl\\""}
C {devices/gnd.sym} -770 120 0 0 {name=l35 lab=GND
value="PWL FILE \\"bit_b3.pwl\\""}
C {devices/vsource.sym} -770 180 0 0 {name=V34 value="PWL FILE \\"bit_b4.pwl\\"" savecurrent=false}
C {devices/lab_pin.sym} -770 150 2 0 {name=p59 lab=B4
value="PWL FILE \\"bit_b4.pwl\\""}
C {devices/gnd.sym} -770 210 0 0 {name=l36 lab=GND
value="PWL FILE \\"bit_b4.pwl\\""}
C {devices/vsource.sym} -770 270 0 0 {name=V35 value="PWL FILE \\"bit_t1.pwl\\"" savecurrent=false}
C {devices/lab_pin.sym} -770 240 2 0 {name=p60 lab=T0
value="PWL FILE \\"bit_t1.pwl\\""}
C {devices/gnd.sym} -770 300 0 0 {name=l37 lab=GND
value="PWL FILE \\"bit_t1.pwl\\""}
C {devices/vsource.sym} -770 360 0 0 {name=V36 value="PWL FILE \\"bit_t2.pwl\\"" savecurrent=false}
C {devices/lab_pin.sym} -770 330 2 0 {name=p61 lab=T1
value="PWL FILE \\"bit_t2.pwl\\""}
C {devices/gnd.sym} -770 390 0 0 {name=l38 lab=GND
value="PWL FILE \\"bit_t2.pwl\\""}
C {devices/vsource.sym} -770 450 0 0 {name=V37 value="PWL FILE \\"bit_t3.pwl\\"" savecurrent=false}
C {devices/lab_pin.sym} -770 420 2 0 {name=p62 lab=T2
value="PWL FILE \\"bit_t3.pwl\\""}
C {devices/gnd.sym} -770 480 0 0 {name=l39 lab=GND
value="PWL FILE \\"bit_t3.pwl\\""}
C {devices/vsource.sym} -770 540 0 0 {name=V38 value="PWL FILE \\"bit_t4.pwl\\"" savecurrent=false}
C {devices/lab_pin.sym} -770 510 2 0 {name=p63 lab=T3
value="PWL FILE \\"bit_t4.pwl\\""}
C {devices/gnd.sym} -770 570 0 0 {name=l40 lab=GND
value="PWL FILE \\"bit_t4.pwl\\""}
C {devices/vsource.sym} -770 630 0 0 {name=V39 value="PWL FILE \\"bit_t5.pwl\\"" savecurrent=false}
C {devices/lab_pin.sym} -770 600 2 0 {name=p64 lab=T4
value="PWL FILE \\"bit_t5.pwl\\""}
C {devices/gnd.sym} -770 660 0 0 {name=l41 lab=GND
value="PWL FILE \\"bit_t5.pwl\\""}
C {devices/vsource.sym} -770 720 0 0 {name=V40 value="PWL FILE \\"bit_t6.pwl\\"" savecurrent=false}
C {devices/lab_pin.sym} -770 690 2 0 {name=p65 lab=T5
value="PWL FILE \\"bit_t6.pwl\\""}
C {devices/gnd.sym} -770 750 0 0 {name=l42 lab=GND
value="PWL FILE \\"bit_t6.pwl\\""}
C {devices/vsource.sym} -770 810 0 0 {name=V41 value="PWL FILE \\"bit_t7.pwl\\"" savecurrent=false}
C {devices/lab_pin.sym} -770 780 2 0 {name=p66 lab=T6
value="PWL FILE \\"bit_t7.pwl\\""}
C {devices/gnd.sym} -770 840 0 0 {name=l43 lab=GND
value="PWL FILE \\"bit_t7.pwl\\""}
C {devices/vsource.sym} -530 -180 0 0 {name=V42 value="PWL FILE \\"bit_b0_n.pwl\\"" savecurrent=false}
C {devices/lab_pin.sym} -530 -210 2 0 {name=p67 lab=B0_n
value="PWL FILE \\"bit_b0_n.pwl\\""}
C {devices/gnd.sym} -530 -150 0 0 {name=l44 lab=GND
value="PWL FILE \\"bit_b0_n.pwl\\""}
C {devices/vsource.sym} -530 -90 0 0 {name=V43 value="PWL FILE \\"bit_b1_n.pwl\\"" savecurrent=false}
C {devices/lab_pin.sym} -530 -120 2 0 {name=p68 lab=B1_n
value="PWL FILE \\"bit_b1_n.pwl\\""}
C {devices/gnd.sym} -530 -60 0 0 {name=l45 lab=GND
value="PWL FILE \\"bit_b1_n.pwl\\""}
C {devices/vsource.sym} -530 0 0 0 {name=V44 value="PWL FILE \\"bit_b2_n.pwl\\"" savecurrent=false}
C {devices/lab_pin.sym} -530 -30 2 0 {name=p69 lab=B2_n
value="PWL FILE \\"bit_b2_n.pwl\\""}
C {devices/gnd.sym} -530 30 0 0 {name=l46 lab=GND
value="PWL FILE \\"bit_b2_n.pwl\\""}
C {devices/vsource.sym} -530 90 0 0 {name=V45 value="PWL FILE \\"bit_b3_n.pwl\\"" savecurrent=false}
C {devices/lab_pin.sym} -530 60 2 0 {name=p70 lab=B3_n
value="PWL FILE \\"bit_b3_n.pwl\\""}
C {devices/gnd.sym} -530 120 0 0 {name=l47 lab=GND
value="PWL FILE \\"bit_b3_n.pwl\\""}
C {devices/vsource.sym} -530 180 0 0 {name=V46 value="PWL FILE \\"bit_b4_n.pwl\\"" savecurrent=false}
C {devices/lab_pin.sym} -530 150 2 0 {name=p71 lab=B4_n
value="PWL FILE \\"bit_b4_n.pwl\\""}
C {devices/gnd.sym} -530 210 0 0 {name=l48 lab=GND
value="PWL FILE \\"bit_b4_n.pwl\\""}
C {devices/vsource.sym} -530 270 0 0 {name=V47 value="PWL FILE \\"bit_t1_n.pwl\\"" savecurrent=false}
C {devices/lab_pin.sym} -530 240 2 0 {name=p72 lab=T0_n
value="PWL FILE \\"bit_t1_n.pwl\\""}
C {devices/gnd.sym} -530 300 0 0 {name=l49 lab=GND
value="PWL FILE \\"bit_t1_n.pwl\\""}
C {devices/vsource.sym} -530 360 0 0 {name=V48 value="PWL FILE \\"bit_t2_n.pwl\\"" savecurrent=false}
C {devices/lab_pin.sym} -530 330 2 0 {name=p73 lab=T1_n
value="PWL FILE \\"bit_t2_n.pwl\\""}
C {devices/gnd.sym} -530 390 0 0 {name=l50 lab=GND
value="PWL FILE \\"bit_t2_n.pwl\\""}
C {devices/vsource.sym} -530 450 0 0 {name=V49 value="PWL FILE \\"bit_t3_n.pwl\\"" savecurrent=false}
C {devices/lab_pin.sym} -530 420 2 0 {name=p74 lab=T2_n
value="PWL FILE \\"bit_t3_n.pwl\\""}
C {devices/gnd.sym} -530 480 0 0 {name=l51 lab=GND
value="PWL FILE \\"bit_t3_n.pwl\\""}
C {devices/vsource.sym} -530 540 0 0 {name=V50 value="PWL FILE \\"bit_t4_n.pwl\\"" savecurrent=false}
C {devices/lab_pin.sym} -530 510 2 0 {name=p75 lab=T3_n
value="PWL FILE \\"bit_t4_n.pwl\\""}
C {devices/gnd.sym} -530 570 0 0 {name=l52 lab=GND
value="PWL FILE \\"bit_t4_n.pwl\\""}
C {devices/vsource.sym} -530 630 0 0 {name=V51 value="PWL FILE \\"bit_t5_n.pwl\\"" savecurrent=false}
C {devices/lab_pin.sym} -530 600 2 0 {name=p76 lab=T4_n
value="PWL FILE \\"bit_t5_n.pwl\\""}
C {devices/gnd.sym} -530 660 0 0 {name=l53 lab=GND
value="PWL FILE \\"bit_t5_n.pwl\\""}
C {devices/vsource.sym} -530 720 0 0 {name=V52 value="PWL FILE \\"bit_t6_n.pwl\\"" savecurrent=false}
C {devices/lab_pin.sym} -530 690 2 0 {name=p77 lab=T5_n
value="PWL FILE \\"bit_t6_n.pwl\\""}
C {devices/gnd.sym} -530 750 0 0 {name=l54 lab=GND
value="PWL FILE \\"bit_t6_n.pwl\\""}
C {devices/vsource.sym} -530 810 0 0 {name=V53 value="PWL FILE \\"bit_t7_n.pwl\\"" savecurrent=false}
C {devices/lab_pin.sym} -530 780 2 0 {name=p78 lab=T6_n
value="PWL FILE \\"bit_t7_n.pwl\\""}
C {devices/gnd.sym} -530 840 0 0 {name=l55 lab=GND
value="PWL FILE \\"bit_t7_n.pwl\\""}
