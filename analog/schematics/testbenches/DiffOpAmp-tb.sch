v {xschem version=3.4.4 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N -360 -30 -340 -30 {
lab=vin_minus}
N -360 10 -340 10 {
lab=vin_plus}
N -470 -10 -420 -10 {
lab=#net1}
N -530 -10 -530 120 {
lab=GND}
N -220 -120 -220 -90 {
lab=#net2}
N -220 70 -220 100 {
lab=GND}
N -220 100 -220 120 {
lab=GND}
N -160 -90 -130 -90 {
lab=GND}
N -130 -90 -130 -80 {
lab=GND}
N -60 10 -40 10 {
lab=voutp}
N 0 -30 20 -30 {
lab=voutm}
N -120 -30 0 -30 {
lab=voutm}
N -120 10 -60 10 {
lab=voutp}
N -420 -80 -420 60 {
lab=#net1}
N -360 10 -360 60 {
lab=vin_plus}
N -360 -80 -360 -30 {
lab=vin_minus}
C {devices/vsource.sym} -500 -10 1 0 {name=V1 value="DC 0.9V" savecurrent=false}
C {devices/code_shown.sym} 160 10 0 0 {name=s1 only_toplevel=false value="
*.ac dec 100 0.1 1G
.tran 10m 1
.control
run
plot vin_plus
let vdiff = voutp - voutm
let dc_gain_val = vdb(vdiff)[0]
echo 'DC_GAIN:' $&dc_gain_val
let gbw_freq = 0
let i = 0
while i < length(vdb(vdiff))
  if vdb(vdiff)[i] <= 0
    let gbw_freq = frequency[i]
    break
  end
  let i = i + 1
end
echo 'GBW:' $&gbw_freq
.endc
"}
C {sky130_fd_pr/corner.sym} 220 -210 0 0 {name=CORNER only_toplevel=false corner=tt}
C {devices/lab_pin.sym} -340 10 3 0 {name=p2 sig_type=std_logic lab=vin_plus}
C {devices/lab_pin.sym} -340 -30 1 0 {name=p3 sig_type=std_logic lab=vin_minus}
C {devices/vsource.sym} -390 -160 3 0 {name=V3 value="DC 0V AC 1mV" savecurrent=false}
C {devices/vsource.sym} -380 180 1 0 {name=V5 value="DC 0V AC 1mV" savecurrent=false}
C {devices/vsource.sym} -250 100 3 0 {name=V6 value="DC 0.7V" savecurrent=false}
C {devices/vsource.sym} -250 -120 1 0 {name=V7 value="DC 0.7V" savecurrent=false}
C {devices/gnd.sym} -530 120 0 0 {name=l2 lab=GND}
C {devices/gnd.sym} -220 120 0 0 {name=l3 lab=GND}
C {devices/gnd.sym} -130 -80 0 0 {name=l4 lab=GND}
C {devices/vsource.sym} -190 -90 3 0 {name=V8 value="DC 1.8V" savecurrent=false}
C {devices/lab_pin.sym} -40 10 1 0 {name=p5 sig_type=std_logic lab=voutp}
C {devices/capa.sym} -60 40 0 0 {name=C2
m=1
value=5p
footprint=1206
device="ceramic capacitor"}
C {devices/gnd.sym} -60 70 0 0 {name=l5 lab=GND}
C {devices/lab_pin.sym} 20 -30 1 0 {name=p6 sig_type=std_logic lab=voutm}
C {devices/capa.sym} 0 0 0 0 {name=C3
m=1
value=5p
footprint=1206
device="ceramic capacitor"}
C {devices/gnd.sym} 0 30 0 0 {name=l7 lab=GND}
C {DiffOpAmp.sym} -160 -10 0 0 {name=x1}
C {spice_probe.sym} -360 -80 0 0 {name=p1 attrs=""}
C {spice_probe.sym} -360 10 0 0 {name=p4 attrs=""}
C {spice_probe.sym} -280 -120 0 0 {name=p7 attrs=""}
C {spice_probe.sym} -220 -120 0 0 {name=p8 attrs=""}
C {spice_probe.sym} -280 100 0 0 {name=p9 attrs=""}
C {spice_probe.sym} -60 10 0 0 {name=p10 attrs=""}
C {spice_probe.sym} 0 -30 0 0 {name=p11 attrs=""}
C {devices/vsource.sym} -390 60 1 0 {name=V2 value="DC 0V AC 1mV 100Hz" savecurrent=false}
C {devices/vsource.sym} -390 -80 3 0 {name=V4 value="DC 0V AC 1mV 100Hz" savecurrent=false}
