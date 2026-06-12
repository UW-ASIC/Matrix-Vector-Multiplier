"""Top-level GEMM testbench — drives full system with generated stimulus.

Supports rigorous PVT testing:
  python tb_gemm_tapeout.py --corner tt,ss,ff --temp -40,27,125
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from testbenches.top.generate_stimulus import (
    generate_stimulus, weights_to_pin_values, input_to_voltage,
)
from components.imc_crossbar.imc_crossbar import generate as imc_generate
from components.interleaved_adc.interleaved_adc import generate as adc_generate
from library.testbenches.base import (
    make_circuit, make_circuit_mc, pwl_spice, print_header, print_result,
    parse_rigor, BACKEND,
)

VDD = 1.8
VREF = 0.9
SIM_TIME = 200e-9

RIGOR_DEFAULTS = {
    "corners": ["tt"],
    "temps": [27],
    "monte_carlo": 0,
    "backend": "ngspice",
}


def build_circuit(stim, vec_idx, corner, temp, mc_seed=None):
    """Build full GEMM testbench circuit for one input vector."""
    if mc_seed is not None:
        ckt = make_circuit_mc("tb_gemm_tapeout", vdd=VDD, temp=temp, seed=mc_seed)
    else:
        ckt = make_circuit("tb_gemm_tapeout", vdd=VDD, corner=corner, temp=temp)

    # Include subcircuits
    ckt.raw_spice(imc_generate())
    ckt.raw_spice(adc_generate())

    # Reference voltage
    ckt.raw_spice(f"Vref vref 0 {VREF}")

    # Weight bits (DC)
    pin_vals = weights_to_pin_values(stim["weights"])
    for pin, val in pin_vals.items():
        ckt.raw_spice(f"V{pin} {pin} 0 {val}")

    # Control: reset HIGH for 40ns, then LOW
    ckt.raw_spice(pwl_spice("xbar_rst", "xbar_rst", "0",
        [(0, VDD), (39.9e-9, VDD), (40e-9, 0), (SIM_TIME, 0)]))

    # ADC go: HIGH from 80ns (slow ramp for convergence)
    ckt.raw_spice(pwl_spice("adc_go", "adc_go", "0",
        [(0, 0), (80e-9, 0), (82e-9, VDD), (SIM_TIME, VDD)]))

    # Inputs: step from 0 to voltage at 50ns
    x_vec = stim["inputs"][vec_idx]
    for i in range(4):
        v = input_to_voltage(x_vec[i])
        ckt.raw_spice(pwl_spice(f"xin{i}", f"xin{i}", "0",
            [(0, 0), (49.9e-9, 0), (50e-9, v), (SIM_TIME, v)]))

    # Crossbar instance
    xbar_x = " ".join(f"xin{i}" for i in range(4))
    xbar_y = " ".join(f"col{j}" for j in range(4))
    wb = " ".join(f"wb_{i}{j}{b}" for i in range(4) for j in range(4) for b in range(4))
    ckt.raw_spice(f"Xxbar {xbar_x} {xbar_y} {wb} xbar_rst vdd 0 imc_crossbar")

    # ADC instance
    cols = " ".join(f"col{j}" for j in range(4))
    adc_d = " ".join(f"adc_d{j}b{b}" for j in range(4) for b in range(4))
    ckt.raw_spice(f"Xadc {cols} vref {adc_d} adc_go vdd 0 interleaved_adc")

    return ckt


def read_adc_codes(result):
    """Read 4-column ADC output codes from simulation result."""
    n = len(result["col0"])
    idx = n - 1
    codes = []
    for j in range(4):
        code = 0
        for b in range(4):
            try:
                v = result[f"adc_d{j}b{b}"][idx]
                if v > VDD / 2:
                    code |= (1 << b)
            except KeyError:
                pass
        codes.append(code)
    return codes


def main():
    config = parse_rigor(RIGOR_DEFAULTS)
    stim = generate_stimulus()
    n_vectors = len(stim["inputs"])

    print_header("GEMM Tapeout — Full System PVT Test")
    print(f"  Corners: {config['corners']}")
    print(f"  Temps: {config['temps']}")
    print(f"  Vectors: {n_vectors}")
    print(f"  Weights: {stim['weights']}")

    all_pass = True
    total_tests = 0
    total_failures = 0

    for corner in config["corners"]:
        for temp in config["temps"]:
            print(f"\n  {'='*50}")
            print(f"  Corner: {corner}, Temp: {temp}C")
            print(f"  {'='*50}")

            for vec_idx in range(n_vectors):
                x_vec = stim["inputs"][vec_idx]
                expected = stim["expected"][vec_idx]

                print(f"\n  [Vector {vec_idx}] Input: {x_vec}")
                ckt = build_circuit(stim, vec_idx, corner, temp)

                sim = ckt.simulator(simulator=BACKEND)
                result = sim.transient(step_time=0.5e-9, end_time=SIM_TIME)
                codes = read_adc_codes(result)

                print(f"  {'Col':<6}{'Code':<8}{'Expected':<10}{'Error':<8}{'Status':<8}")
                print(f"  {'-'*40}")

                vec_pass = True
                for j in range(4):
                    err = abs(codes[j] - expected[j])
                    ok = err <= 1  # allow +/-1 LSB
                    if not ok:
                        vec_pass = False
                        total_failures += 1
                    total_tests += 1
                    print(f"  {j:<6}{codes[j]:<8}{expected[j]:<10}{err:<8}{'PASS' if ok else 'FAIL':<8}")

                all_pass &= vec_pass

    # --- Mismatch corners ---
    mc_runs = config["monte_carlo"]
    mc_failures = 0
    mc_total = 0
    if mc_runs > 0:
        print(f"\n  {'='*50}")
        print(f"  Mismatch Testing: {mc_runs} runs (tt_mm corner)")
        print(f"  {'='*50}")

        for run_idx in range(mc_runs):
            ckt = build_circuit(stim, 0, "tt", 27, mc_seed=run_idx)
            sim = ckt.simulator(simulator=BACKEND)
            result = sim.transient(step_time=0.5e-9, end_time=SIM_TIME)
            codes = read_adc_codes(result)
            expected = stim["expected"][0]
            errors = [abs(codes[j] - expected[j]) for j in range(4)]
            max_err = max(errors)
            mc_total += 4
            fails = sum(1 for e in errors if e > 1)
            mc_failures += fails
            status = "PASS" if fails == 0 else "FAIL"
            print(f"    Run {run_idx:>3}: codes={codes} expected={expected} "
                  f"max_err={max_err} {status}")

        mc_yield = (mc_total - mc_failures) / mc_total * 100 if mc_total > 0 else 100
        print(f"\n    Mismatch Yield: {mc_yield:.1f}% ({mc_total - mc_failures}/{mc_total})")
        if mc_failures > 0:
            all_pass = False
            total_failures += mc_failures
        total_tests += mc_total

    # Summary
    print(f"\n{'='*60}")
    print(f"  PVT SUMMARY")
    print(f"  Corners: {config['corners']}")
    print(f"  Temps: {config['temps']}")
    if mc_runs > 0:
        print(f"  Monte Carlo: {mc_runs} runs")
    print(f"  Total checks: {total_tests}")
    print(f"  Failures: {total_failures}")
    print(f"  Pass rate: {(total_tests - total_failures) / total_tests * 100:.1f}%")
    print(f"\n  OVERALL: {'PASS' if all_pass else 'FAIL'}")
    print(f"{'='*60}\n")
    return all_pass


if __name__ == "__main__":
    main()
