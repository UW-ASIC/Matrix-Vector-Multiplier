v {xschem version=3.4.8RC file_version=1.2}
G {}
K {}
V {}
S {}
F {}
E {}
N -90 -80 -60 -80 {lab=A}
N -90 -40 -60 -40 {lab=B}
N 60 -80 60 -60 {lab=#net1}
N 60 -80 110 -80 {lab=#net1}
N 60 -60 60 -40 {lab=#net1}
N 60 -40 110 -40 {lab=#net1}
N 60 20 60 40 {lab=#net2}
N 60 20 110 20 {lab=#net2}
N 60 40 60 60 {lab=#net2}
N 60 60 110 60 {lab=#net2}
N -90 20 -60 20 {lab=C}
N -90 60 -60 60 {lab=D}
N 230 -60 230 -30 {lab=#net3}
N 230 -30 280 -30 {lab=#net3}
N 230 10 230 40 {lab=#net4}
N 230 10 280 10 {lab=#net4}
N 400 -30 400 -10 {lab=#net5}
N 400 -30 460 -30 {lab=#net5}
N 400 -10 400 10 {lab=#net5}
N 400 10 460 10 {lab=#net5}
N -90 120 630 120 {lab=E}
N 630 80 630 120 {lab=E}
N 580 -10 580 40 {lab=#net6}
N 580 40 630 40 {lab=#net6}
N 750 60 800 60 {lab=xxx}
C {ipin.sym} -90 -80 0 0 {name=p1 lab=A}
C {ipin.sym} -90 -40 0 0 {name=p2 lab=B}
C {ipin.sym} -90 20 0 0 {name=p3 lab=C}
C {ipin.sym} -90 60 0 0 {name=p4 lab=D}
C {ipin.sym} -90 120 0 0 {name=p5 lab=E}
C {sky130_tests/lvnand.sym} -10 -60 0 0 {name=x1 WidthN=1 LenN=0.15 WidthP=1 LenP=0.15 VCCPIN=VCC VSSPIN=VSS m=1}
C {sky130_tests/lvnand.sym} 160 -60 0 0 {name=x2 WidthN=1 LenN=0.15 WidthP=1 LenP=0.15 VCCPIN=VCC VSSPIN=VSS m=1}
C {sky130_tests/lvnand.sym} -10 40 0 0 {name=x3 WidthN=1 LenN=0.15 WidthP=1 LenP=0.15 VCCPIN=VCC VSSPIN=VSS m=1}
C {sky130_tests/lvnand.sym} 160 40 0 0 {name=x4 WidthN=1 LenN=0.15 WidthP=1 LenP=0.15 VCCPIN=VCC VSSPIN=VSS m=1}
C {sky130_tests/lvnand.sym} 330 -10 0 0 {name=x5 WidthN=1 LenN=0.15 WidthP=1 LenP=0.15 VCCPIN=VCC VSSPIN=VSS m=1}
C {sky130_tests/lvnand.sym} 510 -10 0 0 {name=x6 WidthN=1 LenN=0.15 WidthP=1 LenP=0.15 VCCPIN=VCC VSSPIN=VSS m=1}
C {sky130_tests/lvnand.sym} 680 60 0 0 {name=x7 WidthN=1 LenN=0.15 WidthP=1 LenP=0.15 VCCPIN=VCC VSSPIN=VSS m=1}
C {opin.sym} 800 60 0 0 {name=p6 lab=out}
