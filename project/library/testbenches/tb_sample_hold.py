"""Test harness for sample & hold characterization.

Measurements: acquisition time, droop rate, charge injection.
"""
from library.testbenches.base import (
    parse_rigor, fix_xlines, validate_ports, print_header, print_result,
    find_threshold_crossing, make_circuit, BACKEND,
)

REQUIRED_PORTS = [
    "in0", "in1", "in2", "in3",
    "out0", "out1", "out2", "out3",
    "sh_ctrl", "vdd", "vss",
]

RIGOR_DEFAULTS = {
    "corners": ["tt"],
    "temps": [27],
    "monte_carlo": 0,
    "backend": "vacask",
}

from library.pdks import get_pdk as _get_pdk
VDD = _get_pdk().vdd
SIM_TIME = 100e-9
N_CHANNELS = 4


def validate_dut(spice_text: str, subckt_name: str) -> None:
    validate_ports(spice_text, subckt_name, REQUIRED_PORTS)


def run(dut_generate_fn, subckt_name: str, rigor: dict = None):
    config = parse_rigor(rigor or RIGOR_DEFAULTS) if rigor is None else rigor

    spice_text = dut_generate_fn()
    validate_dut(spice_text, subckt_name)
    spice_text = fix_xlines(spice_text)

    print_header(f"{subckt_name} Sample & Hold Characterization")
    all_pass = True

    for corner in config["corners"]:
        for temp in config["temps"]:
            print(f"\n  Corner: {corner}, Temp: {temp}C")

            # --- Test 1: Acquisition time ---
            print("\n  [Acquisition Time]")
            input_voltages = [0.3, 0.5, 0.7, 0.9]
            ckt = make_circuit(f"tb_{subckt_name}_acq", corner=corner, temp=temp)
            ckt.raw_spice(spice_text)
            # VDD already provided by make_circuit
            for i in range(N_CHANNELS):
                ckt.raw_spice(f"Vin{i} in{i} 0 {input_voltages[i]}")
            # sh_ctrl: sample from 5ns to 30ns, then hold
            ckt.PieceWiseLinearVoltageSource(
                name="sh_ctrl", positive="sh_ctrl", negative="0",
                values=[(0, 0), (5e-9, 0), (5.1e-9, VDD), (30e-9, VDD),
                        (30.1e-9, 0), (SIM_TIME, 0)])
            in_ports = " ".join(f"in{i}" for i in range(N_CHANNELS))
            out_ports = " ".join(f"out{i}" for i in range(N_CHANNELS))
            ckt.raw_spice(f"Xdut {in_ports} {out_ports} sh_ctrl vdd 0 {subckt_name}")
            sim = ckt.simulator(simulator=BACKEND)
            result = sim.transient(step_time=0.1e-9, end_time=SIM_TIME)

            # Check that outputs track inputs during sample phase
            # Sample at index ~300 (30ns mark, end of sample phase)
            sample_end_idx = int(30e-9 / 0.1e-9)
            if sample_end_idx >= len(result["out0"]):
                sample_end_idx = len(result["out0"]) - 1

            print(f"  {'Ch':<5}{'Vin':<10}{'Vout@sample':<14}{'Error':<10}")
            print(f"  {'-'*39}")
            acq_pass = True
            for i in range(N_CHANNELS):
                vout = result[f"out{i}"][sample_end_idx]
                error_mv = abs(vout - input_voltages[i]) * 1000
                ok = error_mv < 50  # within 50mV
                if not ok:
                    acq_pass = False
                print(f"  {i:<5}{input_voltages[i]:<10.3f}{vout:<14.4f}"
                      f"{error_mv:<10.1f}mV")
            print_result("    Acquisition error < 50mV", acq_pass)
            all_pass &= acq_pass

            # --- Test 2: Droop rate ---
            print("\n  [Droop Rate]")
            # Measure voltage change during hold phase (30ns to 90ns)
            hold_start_idx = int(31e-9 / 0.1e-9)
            hold_end_idx = int(90e-9 / 0.1e-9)
            if hold_end_idx >= len(result["out0"]):
                hold_end_idx = len(result["out0"]) - 1

            droop_pass = True
            for i in range(N_CHANNELS):
                v_start = result[f"out{i}"][hold_start_idx]
                v_end = result[f"out{i}"][hold_end_idx]
                droop_mv = abs(v_end - v_start) * 1000
                hold_time_ns = (hold_end_idx - hold_start_idx) * 0.1
                droop_rate = droop_mv / hold_time_ns if hold_time_ns > 0 else 0
                ok = droop_rate < 1.0  # < 1 mV/ns
                if not ok:
                    droop_pass = False
                print(f"    Ch{i}: droop = {droop_mv:.2f} mV over {hold_time_ns:.0f} ns"
                      f" ({droop_rate:.3f} mV/ns)")
            print_result("    Droop rate < 1 mV/ns", droop_pass)
            all_pass &= droop_pass

            # --- Test 3: Charge injection ---
            print("\n  [Charge Injection]")
            # Measure output step at sample→hold transition
            pre_hold_idx = int(29.5e-9 / 0.1e-9)
            post_hold_idx = int(32e-9 / 0.1e-9)
            if post_hold_idx >= len(result["out0"]):
                post_hold_idx = len(result["out0"]) - 1

            cinj_pass = True
            for i in range(N_CHANNELS):
                v_pre = result[f"out{i}"][pre_hold_idx]
                v_post = result[f"out{i}"][post_hold_idx]
                injection_mv = abs(v_post - v_pre) * 1000
                ok = injection_mv < 30  # < 30mV
                if not ok:
                    cinj_pass = False
                print(f"    Ch{i}: charge injection = {injection_mv:.1f} mV")
            print_result("    Charge injection < 30mV", cinj_pass)
            all_pass &= cinj_pass

    print(f"\n{'='*60}")
    print(f"  OVERALL: {'PASS' if all_pass else 'FAIL'}")
    print(f"{'='*60}\n")
    return all_pass
