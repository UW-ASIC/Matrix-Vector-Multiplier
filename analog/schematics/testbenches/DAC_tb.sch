v {xschem version=3.4.7 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
B 2 -430 -600 370 -200 {flags=graph
y1=0
y2=2
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=10e-6
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
node=""
color=""
dataset=-1
unitx=1
logx=0
logy=0
}
C {DAC.sym} 10 0 0 0 {name=x1}
C {devices/vsource.sym} -400 -120 0 0 {name=V1 value=1.8 savecurrent=false}
C {devices/lab_pin.sym} -140 -160 0 0 {name=p1 lab=V_in}
C {devices/lab_pin.sym} 160 -160 0 1 {name=p2 lab=I_main}
C {devices/lab_pin.sym} 160 -140 0 1 {name=p3 lab=I_out_n}
C {devices/lab_pin.sym} 160 -120 0 1 {name=p4 lab=I_out_p}
C {devices/lab_pin.sym} -140 -80 0 0 {name=p5 lab=B3}
C {devices/lab_pin.sym} -140 -140 0 0 {name=p6 lab=B0}
C {devices/lab_pin.sym} -140 0 0 0 {name=p7 lab=B7}
C {devices/lab_pin.sym} -140 -60 0 0 {name=p8 lab=B4}
C {devices/lab_pin.sym} -140 -120 0 0 {name=p9 lab=B1}
C {devices/lab_pin.sym} -140 -100 0 0 {name=p10 lab=B2}
C {devices/lab_pin.sym} -140 -40 0 0 {name=p11 lab=B5}
C {devices/lab_pin.sym} -140 -20 0 0 {name=p12 lab=B6}
C {devices/lab_pin.sym} -140 120 0 0 {name=p13 lab=B5_bar}
C {devices/lab_pin.sym} -140 40 0 0 {name=p14 lab=B1_bar}
C {devices/lab_pin.sym} -140 100 0 0 {name=p15 lab=B4_bar}
C {devices/lab_pin.sym} -140 160 0 0 {name=p16 lab=B7_bar}
C {devices/lab_pin.sym} -140 140 0 0 {name=p17 lab=B6_bar}
C {devices/lab_pin.sym} -140 80 0 0 {name=p18 lab=B3_bar}
C {devices/lab_pin.sym} -140 60 0 0 {name=p19 lab=B2_bar}
C {devices/lab_pin.sym} -140 20 0 0 {name=p20 lab=B0_bar}
C {devices/lab_pin.sym} -400 -150 2 0 {name=p21 lab=V_in}
C {devices/gnd.sym} -400 -90 0 0 {name=l1 lab=GND}
C {sky130_fd_pr/corner.sym} 320 -150 0 0 {name=CORNER only_toplevel=false corner=tt}
C {devices/res.sym} 260 140 0 0 {name=R1
value=1k
footprint=1206
device=resistor
m=1}
C {devices/lab_pin.sym} 260 110 0 1 {name=p22 lab=I_out_p}
C {devices/res.sym} 360 140 0 0 {name=R2
value=1k
footprint=1206
device=resistor
m=1}
C {devices/lab_pin.sym} 360 110 0 1 {name=p23 lab=I_out_n}
C {devices/gnd.sym} 260 170 0 0 {name=l2 lab=GND}
C {devices/gnd.sym} 360 170 0 0 {name=l3 lab=GND}
C {devices/res.sym} 460 140 0 0 {name=R3
value=1k
footprint=1206
device=resistor
m=1}
C {devices/gnd.sym} 460 170 0 0 {name=l4 lab=GND}
C {devices/lab_pin.sym} 460 110 0 1 {name=p24 lab=I_main}
C {devices/launcher.sym} 490 -570 0 0 {name=h5
descr="load waves" 
tclcommand="xschem raw_read $netlist_dir/DAC_tb.raw tran"
}
