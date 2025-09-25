v {xschem version=3.4.4 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 1400 40 1400 250 {
lab=#net1}
N 1140 40 1140 240 {
lab=#net2}
N 880 40 880 240 {
lab=#net3}
N 620 40 620 240 {
lab=#net4}
N 340 40 340 240 {
lab=#net5}
N 80 40 80 240 {
lab=#net6}
N 80 -40 180 -40 {
lab=#net7}
N 340 -40 460 -40 {
lab=#net8}
N 620 -40 720 -40 {
lab=#net9}
N 880 -40 980 -40 {
lab=#net10}
N 1140 -40 1240 -40 {
lab=#net11}
N 1200 40 1240 40 {
lab=CLK}
N 1200 -160 1200 40 {
lab=CLK}
N 940 40 980 40 {
lab=CLK}
N 940 -160 940 40 {
lab=CLK}
N 680 40 720 40 {
lab=CLK}
N 680 -160 680 40 {
lab=CLK}
N 420 40 460 40 {
lab=CLK}
N 420 -160 420 40 {
lab=CLK}
N 140 40 180 40 {
lab=CLK}
N 140 -160 140 40 {
lab=CLK}
N -120 40 -80 40 {
lab=CLK}
N -120 -160 -120 40 {
lab=CLK}
N -120 -160 140 -160 {
lab=CLK}
N 140 -160 420 -160 {
lab=CLK}
N 420 -160 680 -160 {
lab=CLK}
N 680 -160 940 -160 {
lab=CLK}
N 940 -160 1200 -160 {
lab=CLK}
N -160 -80 -10 -80 {
lab=nRESET}
N -160 -80 -160 120 {
lab=nRESET}
N -160 120 1310 120 {
lab=nRESET}
N 1310 80 1310 120 {
lab=nRESET}
N 1050 80 1050 120 {
lab=nRESET}
N 790 80 790 120 {
lab=nRESET}
N 530 80 530 120 {
lab=nRESET}
N 250 80 250 120 {
lab=nRESET}
N -10 80 -10 120 {
lab=nRESET}
N 1040 280 1070 280 {
lab=COMP}
N 1040 140 1040 280 {
lab=COMP}
N 780 280 810 280 {
lab=COMP}
N 780 140 780 280 {
lab=COMP}
N 520 280 550 280 {
lab=COMP}
N 520 140 520 280 {
lab=COMP}
N 240 280 270 280 {
lab=COMP}
N 240 140 240 280 {
lab=COMP}
N -20 280 10 280 {
lab=COMP}
N -20 140 -20 280 {
lab=COMP}
N 780 140 1040 140 {
lab=COMP}
N 520 140 780 140 {
lab=COMP}
N 240 140 520 140 {
lab=COMP}
N -20 140 240 140 {
lab=COMP}
N -160 140 -20 140 {
lab=COMP}
N 1400 400 1400 440 {
lab=nRESET}
N -140 440 1400 440 {
lab=nRESET}
N -140 120 -140 440 {
lab=nRESET}
N 80 400 80 440 {
lab=nRESET}
N 340 400 340 440 {
lab=nRESET}
N 620 400 620 440 {
lab=nRESET}
N 880 400 880 440 {
lab=nRESET}
N 1140 400 1140 440 {
lab=nRESET}
N 1330 360 1330 390 {
lab=GND}
N 1330 280 1330 360 {
lab=GND}
N 1490 280 1540 280 {
lab=#net12}
N 1540 280 1540 490 {
lab=#net12}
N 1070 490 1540 490 {
lab=#net12}
N 1070 360 1070 490 {
lab=#net12}
N 1230 280 1300 280 {
lab=D0}
N 1300 280 1300 520 {
lab=D0}
N 810 520 1300 520 {
lab=D0}
N 810 360 810 520 {
lab=D0}
N 970 280 1020 280 {
lab=D1}
N 1020 280 1020 540 {
lab=D1}
N 550 540 1020 540 {
lab=D1}
N 550 360 550 540 {
lab=D1}
N 710 280 760 280 {
lab=D2}
N 760 280 760 560 {
lab=D2}
N 270 560 760 560 {
lab=D2}
N 270 360 270 560 {
lab=D2}
N 430 280 500 280 {
lab=D3}
N 500 280 500 580 {
lab=D3}
N 10 580 500 580 {
lab=D3}
N 10 360 10 580 {
lab=D3}
N 170 280 220 280 {
lab=VoutY}
N 220 280 220 620 {
lab=VoutY}
N 500 580 500 620 {
lab=D3}
N 760 560 760 620 {
lab=D2}
N 1020 540 1020 620 {
lab=D1}
N 1300 520 1300 620 {
lab=D0}
C {DFF-async-nSet-nReset.sym} 0 0 0 0 {name=x2}
C {DFF-async-nSet-nReset.sym} 260 0 0 0 {name=x3}
C {DFF-async-nSet-nReset.sym} 540 0 0 0 {name=x4}
C {DFF-async-nSet-nReset.sym} 800 0 0 0 {name=x5}
C {DFF-async-nSet-nReset.sym} 1060 0 0 0 {name=x6}
C {DFF-async-nSet-nReset.sym} 1320 0 0 0 {name=x7}
C {gnd.sym} 10 80 0 0 {name=l1 lab=GND}
C {gnd.sym} 270 80 0 0 {name=l2 lab=GND}
C {gnd.sym} 550 80 0 0 {name=l3 lab=GND}
C {gnd.sym} 810 80 0 0 {name=l4 lab=GND}
C {gnd.sym} 1070 80 0 0 {name=l5 lab=GND}
C {gnd.sym} 1330 80 0 0 {name=l6 lab=GND}
C {vdd.sym} 10 -80 0 0 {name=l7 lab=VDD}
C {vdd.sym} 270 -80 0 0 {name=l8 lab=VDD}
C {vdd.sym} 550 -80 0 0 {name=l9 lab=VDD}
C {vdd.sym} 810 -80 0 0 {name=l10 lab=VDD}
C {vdd.sym} 1070 -80 0 0 {name=l11 lab=VDD}
C {vdd.sym} 1330 -80 0 0 {name=l12 lab=VDD}
C {DFF-async-nSet-nReset.sym} 90 320 0 0 {name=x8}
C {DFF-async-nSet-nReset.sym} 350 320 0 0 {name=x9}
C {DFF-async-nSet-nReset.sym} 630 320 0 0 {name=x10}
C {DFF-async-nSet-nReset.sym} 890 320 0 0 {name=x11}
C {DFF-async-nSet-nReset.sym} 1150 320 0 0 {name=x12}
C {DFF-async-nSet-nReset.sym} 1410 320 0 0 {name=x13}
C {gnd.sym} 100 400 0 0 {name=l13 lab=GND}
C {gnd.sym} 360 400 0 0 {name=l14 lab=GND}
C {gnd.sym} 640 400 0 0 {name=l15 lab=GND}
C {gnd.sym} 900 400 0 0 {name=l16 lab=GND}
C {gnd.sym} 1160 400 0 0 {name=l17 lab=GND}
C {gnd.sym} 1420 400 0 0 {name=l18 lab=GND}
C {vdd.sym} 100 240 0 0 {name=l19 lab=VDD}
C {vdd.sym} 360 240 0 0 {name=l20 lab=VDD}
C {vdd.sym} 640 240 0 0 {name=l21 lab=VDD}
C {vdd.sym} 900 240 0 0 {name=l22 lab=VDD}
C {vdd.sym} 1160 240 0 0 {name=l23 lab=VDD}
C {vdd.sym} 1420 240 0 0 {name=l24 lab=VDD}
C {gnd.sym} -80 -40 0 0 {name=l25 lab=GND}
C {ipin.sym} -120 -160 0 0 {name=p4 lab=CLK}
C {ipin.sym} -160 120 0 0 {name=p1 lab=nRESET}
C {ipin.sym} -160 140 0 0 {name=p2 lab=COMP}
C {gnd.sym} 1330 390 0 0 {name=l26 lab=GND}
C {gnd.sym} -220 -220 0 0 {name=l27 lab=GND}
C {vdd.sym} -220 -270 0 0 {name=l28 lab=VDD}
C {ipin.sym} -220 -220 0 0 {name=p3 lab=GND}
C {ipin.sym} -220 -270 0 0 {name=p5 lab=VDD}
C {opin.sym} 1300 620 0 0 {name=p7 lab=D0}
C {opin.sym} 1020 620 0 0 {name=p6 lab=D1}
C {opin.sym} 760 620 0 0 {name=p8 lab=D2}
C {opin.sym} 500 620 0 0 {name=p9 lab=D3}
C {opin.sym} 220 620 0 0 {name=p10 lab=D4}
