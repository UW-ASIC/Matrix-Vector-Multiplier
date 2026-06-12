"""Test harness for DAC characterization.

Measurements: DNL/INL (step all codes), monotonicity, settling time.
"""
from library.testbenches.base import (
    parse_rigor, fix_xlines, validate_ports, print_header, print_result,
    make_circuit, pwl_spice, BACKEND,
)

REQUIRED_PORTS = ["vref", "b0", "b1", "b2", "b3", "out", "vdd", "vss"]

RIGOR_DEFAULTS = {
    "corners": ["tt"],
    "temps": [27],
    "monte_carlo": 0,
    "backend": "vacask",
}

from library.pdks import get_pdk as _get_pdk
VDD = _get_pdk().vdd
VREF = VDD / 2
N_BITS = 4
N_CODES = 2 ** N_BITS
SETTLE_TIME = 20e-9
CODE_PERIOD = 30e-9
BIT_STEP_TIME = 5e-9  # bits step at this time (charge-redistribution DAC needs a transient)


def validate_dut(spice_text: str, subckt_name: str) -> None:
    validate_ports(spice_text, subckt_name, REQUIRED_PORTS)


def run(dut_generate_fn, subckt_name: str, rigor: dict = None):
    config = parse_rigor(rigor or RIGOR_DEFAULTS) if rigor is None else rigor

    spice_text = dut_generate_fn()
    validate_dut(spice_text, subckt_name)
    spice_text = fix_xlines(spice_text)

    print_header(f"{subckt_name} DAC Characterization")
    all_pass = True

    for corner in config["corners"]:
        for temp in config["temps"]:
            print(f"\n  Corner: {corner}, Temp: {temp}C")

            # --- Test 1: DNL/INL (step through all codes) ---
            print("\n  [DNL/INL - All Codes]")
            print(f"  {'Code':<6}{'Vout':<12}{'Ideal':<12}{'DNL':<10}{'INL':<10}")
            print(f"  {'-'*50}")

            voltages = []

            for code in range(N_CODES):
                sim_time = BIT_STEP_TIME + SETTLE_TIME + 5e-9
                ckt = make_circuit(f"tb_{subckt_name}_code{code}", corner=corner, temp=temp)
                ckt.raw_spice(spice_text)
                # VDD already provided by make_circuit
                ckt.raw_spice(f"Vref vref 0 {VREF}")
                # Step bits from 0 to target (charge-redistribution needs transient)
                for b in range(N_BITS):
                    bval = VDD if (code >> b) & 1 else 0
                    ckt.raw_spice(pwl_spice(f"b{b}", f"b{b}", "0",
                        [(0, 0), (BIT_STEP_TIME - 0.1e-9, 0),
                         (BIT_STEP_TIME, bval), (sim_time, bval)]))
                # Load capacitor on output
                ckt.raw_spice("Cload out 0 100f")
                ckt.raw_spice(f"Xdut vref b0 b1 b2 b3 out vdd 0 {subckt_name}")
                sim = ckt.simulator(simulator=BACKEND)
                result = sim.transient(step_time=0.5e-9, end_time=sim_time)
                vout = result["out"][-1]
                voltages.append(vout)

            # Compute DNL/INL using endpoint-fit LSB
            dnl_values = []
            inl_values = []
            inl_accum = 0.0
            # Endpoint-fit: LSB = (V[max] - V[0]) / (N-1)
            lsb_ideal = (voltages[-1] - voltages[0]) / (N_CODES - 1) if voltages[-1] != voltages[0] else VREF / N_CODES

            for code in range(N_CODES):
                v_ideal = voltages[0] + code * lsb_ideal
                if code > 0:
                    step = voltages[code] - voltages[code - 1]
                    dnl = (step / lsb_ideal) - 1.0
                else:
                    dnl = 0.0
                inl_accum += dnl if code > 0 else 0
                dnl_values.append(dnl)
                inl_values.append(inl_accum)
                print(f"  {code:<6}{voltages[code]:<12.4f}{v_ideal:<12.4f}"
                      f"{dnl:<10.3f}{inl_accum:<10.3f}")

            max_dnl = max(abs(d) for d in dnl_values)
            max_inl = max(abs(i) for i in inl_values)
            dnl_pass = max_dnl < 1.0
            inl_pass = max_inl < 1.0
            print(f"\n    Max |DNL|: {max_dnl:.3f} LSB")
            print(f"    Max |INL|: {max_inl:.3f} LSB")
            print_result("    DNL < 1 LSB", dnl_pass)
            print_result("    INL < 1 LSB", inl_pass)
            all_pass &= dnl_pass
            all_pass &= inl_pass

            # --- Test 2: Monotonicity ---
            print("\n  [Monotonicity]")
            monotonic = all(voltages[i] <= voltages[i + 1]
                           for i in range(len(voltages) - 1))
            print_result("    Monotonic", monotonic)
            all_pass &= monotonic

            # --- Test 3: Settling time ---
            print("\n  [Settling Time]")
            # Measure settling for mid-code transition (0→8)
            ckt = make_circuit(f"tb_{subckt_name}_settle", corner=corner, temp=temp)
            ckt.raw_spice(spice_text)
            # VDD already provided by make_circuit
            ckt.raw_spice(f"Vref vref 0 {VREF}")
            # Start at code 0, switch to code 8 at 5ns
            target_code = N_CODES // 2
            for b in range(N_BITS):
                bval = VDD if (target_code >> b) & 1 else 0
                ckt.raw_spice(pwl_spice(f"b{b}", f"b{b}", "0",
                    [(0, 0), (5e-9, 0), (5.1e-9, bval), (50e-9, bval)]))
            ckt.raw_spice("Cload out 0 100f")
            ckt.raw_spice(f"Xdut vref b0 b1 b2 b3 out vdd 0 {subckt_name}")
            sim = ckt.simulator(simulator=BACKEND)
            result = sim.transient(step_time=0.1e-9, end_time=50e-9)
            out_data = list(result["out"])
            final_v = out_data[-1]
            # Find when output settles within 0.5 LSB of final
            settle_threshold = 0.5 * lsb_ideal
            settle_idx = None
            for i in range(len(out_data) - 1, 0, -1):
                if abs(out_data[i] - final_v) > settle_threshold:
                    settle_idx = i + 1
                    break
            if settle_idx:
                settle_ns = settle_idx * 0.1  # step_time in ns
                settle_pass = settle_ns < 15.0
                print(f"    Settling time (0→{target_code}): {settle_ns:.1f} ns")
                print_result("    Settle < 15ns", settle_pass)
                all_pass &= settle_pass
            else:
                print("    Output already settled (instant)")
                print_result("    Settle OK", True)

    print(f"\n{'='*60}")
    print(f"  OVERALL: {'PASS' if all_pass else 'FAIL'}")
    print(f"{'='*60}\n")
    return all_pass
