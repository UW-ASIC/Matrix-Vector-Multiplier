"""Test harness for IMC crossbar characterization.

Measurements: MAC linearity (R^2), compute SNR, crosstalk.
"""
import math

from library.testbenches.base import (
    parse_rigor, fix_xlines, validate_ports, print_header, print_result,
    make_circuit, BACKEND,
)

N_ROWS = 4
N_COLS = 4
WEIGHT_BITS = 4

REQUIRED_PORTS = (
    [f"x{i}" for i in range(N_ROWS)]
    + [f"y{j}" for j in range(N_COLS)]
    + [f"wb_{i}{j}{b}" for i in range(N_ROWS) for j in range(N_COLS) for b in range(WEIGHT_BITS)]
    + ["rst", "vdd", "vss"]
)

RIGOR_DEFAULTS = {
    "corners": ["tt"],
    "temps": [27],
    "monte_carlo": 0,
    "backend": "vacask",
}

from library.pdks import get_pdk as _get_pdk
_pdk = _get_pdk()
VDD = _pdk.vdd
VREF = VDD / 2
SIM_TIME = 80e-9


def validate_dut(spice_text: str, subckt_name: str) -> None:
    validate_ports(spice_text, subckt_name, REQUIRED_PORTS)


def _compute_expected_voltage(weights_col, inputs, vref, c_unit, c_int, n_bits):
    """Compute expected column voltage from charge sharing.

    Cap array is binary-weighted: bit b has c_unit * 2^b.
    So effective cap for weight w = w * c_unit (the integer value).
    """
    total_weight_cap = sum(w * c_unit for w in weights_col)
    total_charge = sum(inputs[i] * weights_col[i] * c_unit for i in range(len(inputs)))
    total_cap = c_int + total_weight_cap
    return total_charge / total_cap if total_cap > 0 else 0


def run(dut_generate_fn, subckt_name: str, rigor: dict = None):
    config = parse_rigor(rigor or RIGOR_DEFAULTS) if rigor is None else rigor

    spice_text = dut_generate_fn()
    validate_dut(spice_text, subckt_name)
    spice_text = fix_xlines(spice_text)

    print_header(f"{subckt_name} IMC Crossbar Characterization")
    all_pass = True

    # Parameters from the active PDK
    c_unit = _pdk.caps["c_unit"]
    c_int = _pdk.caps["c_int"]

    for corner in config["corners"]:
        for temp in config["temps"]:
            print(f"\n  Corner: {corner}, Temp: {temp}C")

            # --- Test 1: MAC Linearity ---
            print("\n  [MAC Linearity - R^2]")
            # Test with various weight/input combinations
            test_cases = [
                # (weights per column j=0, input voltages)
                ([1, 2, 4, 8], [0.2, 0.4, 0.6, 0.8]),
                ([15, 0, 0, 0], [0.9, 0.0, 0.0, 0.0]),
                ([7, 7, 7, 7], [0.45, 0.45, 0.45, 0.45]),
                ([3, 6, 9, 12], [0.3, 0.5, 0.7, 0.9]),
                ([0, 0, 0, 15], [0.0, 0.0, 0.0, 0.9]),
            ]

            measured = []
            expected = []

            for weights_col0, inputs in test_cases:
                ckt = make_circuit(f"tb_{subckt_name}_lin", corner=corner, temp=temp)
                ckt.raw_spice(spice_text)
                # VDD already provided by make_circuit

                # Weight bits: set column 0 weights, others to 0
                for i in range(N_ROWS):
                    for j in range(N_COLS):
                        for b in range(WEIGHT_BITS):
                            if j == 0:
                                wval = VDD if (weights_col0[i] >> b) & 1 else 0
                            else:
                                wval = 0
                            ckt.raw_spice(f"Vwb_{i}{j}{b} wb_{i}{j}{b} 0 {wval}")

                # Reset: HIGH 0-30ns, then LOW
                ckt.PieceWiseLinearVoltageSource(
                    name="rst", positive="rst", negative="0",
                    values=[(0, VDD), (30e-9, VDD), (30.1e-9, 0), (SIM_TIME, 0)])

                # Inputs: step to target at 40ns (after reset drops)
                for i in range(N_ROWS):
                    ckt.PieceWiseLinearVoltageSource(
                        name=f"x{i}", positive=f"x{i}", negative="0",
                        values=[(0, 0), (40e-9, 0), (40.1e-9, inputs[i]),
                                (SIM_TIME, inputs[i])])

                # Instantiate
                row_ports = " ".join(f"x{i}" for i in range(N_ROWS))
                col_ports = " ".join(f"y{j}" for j in range(N_COLS))
                wb_ports = " ".join(
                    f"wb_{i}{j}{b}"
                    for i in range(N_ROWS) for j in range(N_COLS)
                    for b in range(WEIGHT_BITS))
                ckt.raw_spice(
                    f"Xdut {row_ports} {col_ports} {wb_ports} rst vdd 0 {subckt_name}")

                sim = ckt.simulator(simulator=BACKEND)
                result = sim.transient(step_time=0.5e-9, end_time=SIM_TIME)
                v_meas = result["y0"][-1]
                v_exp = _compute_expected_voltage(
                    weights_col0, inputs, VREF, c_unit, c_int, WEIGHT_BITS)
                measured.append(v_meas)
                expected.append(v_exp)

            # Compute R^2
            if len(measured) > 1:
                mean_m = sum(measured) / len(measured)
                mean_e = sum(expected) / len(expected)
                ss_res = sum((m - e) ** 2 for m, e in zip(measured, expected))
                ss_tot = sum((m - mean_m) ** 2 for m in measured)
                r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0
            else:
                r_squared = 0

            print(f"  {'Test':<6}{'Measured':<12}{'Expected':<12}{'Error':<10}")
            print(f"  {'-'*40}")
            for i, (m, e) in enumerate(zip(measured, expected)):
                err_mv = (m - e) * 1000
                print(f"  {i:<6}{m:<12.4f}{e:<12.4f}{err_mv:<10.1f}mV")
            print(f"\n    R^2 = {r_squared:.6f}")
            r2_pass = r_squared > 0.95
            print_result("    R^2 > 0.95", r2_pass)
            all_pass &= r2_pass

            # --- Test 2: Compute SNR ---
            print("\n  [Compute SNR]")
            errors_v = [abs(m - e) for m, e in zip(measured, expected)]
            signal_rms = math.sqrt(sum(e ** 2 for e in expected) / len(expected))
            noise_rms = math.sqrt(sum(err ** 2 for err in errors_v) / len(errors_v))
            if noise_rms > 0:
                snr_db = 20 * math.log10(signal_rms / noise_rms)
            else:
                snr_db = 100.0  # perfect
            snr_pass = snr_db > 30.0
            print(f"    Signal RMS: {signal_rms * 1000:.2f} mV")
            print(f"    Noise RMS:  {noise_rms * 1000:.2f} mV")
            print(f"    SNR: {snr_db:.1f} dB")
            print_result("    SNR > 30 dB", snr_pass)
            all_pass &= snr_pass

            # --- Test 3: Crosstalk ---
            print("\n  [Crosstalk]")
            # Drive col0 with max weight, check col1 stays near 0
            ckt = make_circuit(f"tb_{subckt_name}_xtalk", corner=corner, temp=temp)
            ckt.raw_spice(spice_text)
            # VDD already provided by make_circuit
            # All weight bits for col0 row0 = 15, col1 all zeros
            for i in range(N_ROWS):
                for j in range(N_COLS):
                    for b in range(WEIGHT_BITS):
                        if j == 0 and i == 0:
                            wval = VDD
                        else:
                            wval = 0
                        ckt.raw_spice(f"Vwb_{i}{j}{b} wb_{i}{j}{b} 0 {wval}")
            ckt.PieceWiseLinearVoltageSource(
                name="rst", positive="rst", negative="0",
                values=[(0, VDD), (30e-9, VDD), (30.1e-9, 0), (SIM_TIME, 0)])
            for i in range(N_ROWS):
                v_in = VREF if i == 0 else 0
                ckt.PieceWiseLinearVoltageSource(
                    name=f"x{i}", positive=f"x{i}", negative="0",
                    values=[(0, 0), (40e-9, 0), (40.1e-9, v_in), (SIM_TIME, v_in)])
            ckt.raw_spice(
                f"Xdut {row_ports} {col_ports} {wb_ports} rst vdd 0 {subckt_name}")
            sim = ckt.simulator(simulator=BACKEND)
            result = sim.transient(step_time=0.5e-9, end_time=SIM_TIME)
            y0_v = result["y0"][-1]
            y1_v = result["y1"][-1]
            crosstalk_mv = abs(y1_v) * 1000
            xtalk_pass = crosstalk_mv < 10.0
            print(f"    y0 (active): {y0_v * 1000:.1f} mV")
            print(f"    y1 (idle):   {y1_v * 1000:.1f} mV (crosstalk)")
            print_result("    Crosstalk < 10mV", xtalk_pass)
            all_pass &= xtalk_pass

    print(f"\n{'='*60}")
    print(f"  OVERALL: {'PASS' if all_pass else 'FAIL'}")
    print(f"{'='*60}\n")
    return all_pass
