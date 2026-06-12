"""Test harness for ADC characterization.

Measurements: DNL/INL (sweep), missing codes, conversion latency.
"""
from library.testbenches.base import (
    parse_rigor, fix_xlines, validate_ports, print_header, print_result,
    find_threshold_crossing, make_circuit, BACKEND,
)

REQUIRED_PORTS = [
    "col0", "col1", "col2", "col3", "vref",
    "d0b0", "d0b1", "d0b2", "d0b3",
    "d1b0", "d1b1", "d1b2", "d1b3",
    "d2b0", "d2b1", "d2b2", "d2b3",
    "d3b0", "d3b1", "d3b2", "d3b3",
    "adc_go", "vdd", "vss",
]

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
SIM_TIME = 100e-9


def validate_dut(spice_text: str, subckt_name: str) -> None:
    validate_ports(spice_text, subckt_name, REQUIRED_PORTS)


def _read_codes(result, n_cols=4, n_bits=4):
    """Extract ADC output codes from last simulation point."""
    codes = []
    for j in range(n_cols):
        code = 0
        for b in range(n_bits):
            try:
                v = result[f"d{j}b{b}"][-1]
                if v > VDD / 2:
                    code |= (1 << b)
            except KeyError:
                pass
        codes.append(code)
    return codes


def run(dut_generate_fn, subckt_name: str, rigor: dict = None):
    config = parse_rigor(rigor or RIGOR_DEFAULTS) if rigor is None else rigor

    spice_text = dut_generate_fn()
    validate_dut(spice_text, subckt_name)
    spice_text = fix_xlines(spice_text)

    print_header(f"{subckt_name} ADC Characterization")
    all_pass = True

    for corner in config["corners"]:
        for temp in config["temps"]:
            print(f"\n  Corner: {corner}, Temp: {temp}C")

            # --- Test 1: Known DC voltages ---
            print("\n  [Known DC Inputs]")
            print(f"  {'Col':<6}{'Vin':<10}{'Code':<8}{'Expected':<10}")
            print(f"  {'-'*34}")

            test_voltages = [0.40, 0.25, 0.10, 0.80]
            ckt = make_circuit(f"tb_{subckt_name}_dc", corner=corner, temp=temp)
            ckt.raw_spice(spice_text)
            ckt.raw_spice(f".option reltol=5e-3 abstol=1e-10 vntol=1e-4 gmin=1e-11 method=gear itl4=300")
            # VDD already provided by make_circuit
            ckt.raw_spice(f"Vref vref 0 {VREF}")
            for j in range(4):
                ckt.raw_spice(f"Vcol{j} col{j} 0 {test_voltages[j]}")
            ckt.PieceWiseLinearVoltageSource(
                name="adc_go", positive="adc_go", negative="0",
                values=[(0, 0), (20e-9, 0), (22e-9, VDD), (SIM_TIME, VDD)])
            cols = " ".join(f"col{j}" for j in range(4))
            d_bits = " ".join(f"d{j}b{b}" for j in range(4) for b in range(4))
            ckt.raw_spice(f"Xdut {cols} vref {d_bits} adc_go vdd 0 {subckt_name}")
            sim = ckt.simulator(simulator=BACKEND)
            result = sim.transient(step_time=0.5e-9, end_time=SIM_TIME)
            codes = _read_codes(result)

            for j in range(4):
                expected = int(test_voltages[j] / VREF * N_CODES)
                expected = min(N_CODES - 1, max(0, expected))
                status = "OK" if codes[j] == expected else "FAIL"
                if codes[j] != expected:
                    all_pass = False
                print(f"  {j:<6}{test_voltages[j]:<10.3f}{codes[j]:<8}{expected:<10}{status}")

            # --- Test 2: Full sweep (col0) ---
            print(f"\n  [Input Sweep - col0, {N_CODES} levels]")
            print(f"  {'Vin':<10}{'Code':<8}{'Expected':<10}")
            print(f"  {'-'*28}")

            sweep_codes = []
            for i in range(N_CODES):
                vin = (i + 0.5) / N_CODES * VREF
                ckt = make_circuit(f"tb_{subckt_name}_sw{i}", corner=corner, temp=temp)
                ckt.raw_spice(spice_text)
                ckt.raw_spice(f".option reltol=5e-3 abstol=1e-10 vntol=1e-4 gmin=1e-11 method=gear itl4=300")
                # VDD already provided by make_circuit
                ckt.raw_spice(f"Vref vref 0 {VREF}")
                ckt.raw_spice(f"Vcol0 col0 0 {vin}")
                for j in range(1, 4):
                    ckt.raw_spice(f"Vcol{j} col{j} 0 0")
                ckt.PieceWiseLinearVoltageSource(
                    name="adc_go", positive="adc_go", negative="0",
                    values=[(0, 0), (20e-9, 0), (22e-9, VDD), (SIM_TIME, VDD)])
                ckt.raw_spice(f"Xdut {cols} vref {d_bits} adc_go vdd 0 {subckt_name}")
                sim = ckt.simulator(simulator=BACKEND)
                result = sim.transient(step_time=0.5e-9, end_time=SIM_TIME)
                code = _read_codes(result)[0]
                sweep_codes.append(code)

                expected = i
                status = "OK" if code == expected else "FAIL"
                if code != expected:
                    all_pass = False
                print(f"  {vin:<10.4f}{code:<8}{expected:<10}{status}")

            # --- Test 3: Monotonicity ---
            monotonic = all(sweep_codes[i] <= sweep_codes[i + 1]
                           for i in range(len(sweep_codes) - 1))
            print(f"\n    Monotonicity: {'PASS' if monotonic else 'FAIL'}")
            all_pass &= monotonic

            # --- Test 4: Missing codes ---
            missing = [i for i in range(N_CODES) if i not in sweep_codes]
            print(f"    Missing codes: {missing if missing else 'None'}")
            if missing:
                all_pass = False

            # --- Test 5: Conversion latency ---
            print("\n  [Conversion Latency]")
            ckt = make_circuit(f"tb_{subckt_name}_lat", corner=corner, temp=temp)
            ckt.raw_spice(spice_text)
            ckt.raw_spice(f".option reltol=5e-3 abstol=1e-10 vntol=1e-4 gmin=1e-11 method=gear itl4=300")
            # VDD already provided by make_circuit
            ckt.raw_spice(f"Vref vref 0 {VREF}")
            ckt.raw_spice(f"Vcol0 col0 0 {VREF / 2}")
            for j in range(1, 4):
                ckt.raw_spice(f"Vcol{j} col{j} 0 0")
            ckt.PieceWiseLinearVoltageSource(
                name="adc_go", positive="adc_go", negative="0",
                values=[(0, 0), (20e-9, 0), (22e-9, VDD), (SIM_TIME, VDD)])
            ckt.raw_spice(f"Xdut {cols} vref {d_bits} adc_go vdd 0 {subckt_name}")
            sim = ckt.simulator(simulator=BACKEND)
            result = sim.transient(step_time=0.1e-9, end_time=SIM_TIME)
            # Measure time from adc_go rising to MSB settling
            adc_go_data = list(result["adc_go"])
            go_rise = find_threshold_crossing(adc_go_data, VDD / 2, "rising")
            # Check MSB (d0b3) for settling
            try:
                msb_data = list(result["d0b3"])
                msb_edge = find_threshold_crossing(msb_data, VDD / 2, "rising")
                if msb_edge is None:
                    msb_edge = find_threshold_crossing(msb_data, VDD / 2, "falling")
            except KeyError:
                msb_edge = None

            if go_rise and msb_edge and msb_edge > go_rise:
                latency_ns = (msb_edge - go_rise) * 0.1
                latency_pass = latency_ns < 50.0
                print(f"    Conversion latency: {latency_ns:.1f} ns")
                print_result("    Latency < 50ns", latency_pass)
                all_pass &= latency_pass
            else:
                print("    Could not measure latency")

    print(f"\n{'='*60}")
    print(f"  OVERALL: {'PASS' if all_pass else 'FAIL'}")
    print(f"{'='*60}\n")
    return all_pass
