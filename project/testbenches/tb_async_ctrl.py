"""Testbench for async compute controller.

Verifies self-timed sequencing: GO pulse -> xbar_rst -> settle -> adc_go -> done.
Measures phase durations and checks correct ordering.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.async_ctrl.async_ctrl import generate
from library.testbenches.base import (
    fix_xlines, print_header, print_result, find_threshold_crossing, make_circuit,
    BACKEND,
)
from library.pdks import get_pdk

_pdk = get_pdk()
VDD = _pdk.vdd
SIM_TIME = 100e-9


def run_timing_test():
    spice_text = generate()
    spice_text = fix_xlines(spice_text)

    print_header("async_ctrl Timing Verification")

    ckt = make_circuit("tb_async_ctrl")
    ckt.raw_spice(spice_text)

    # GO pulse: rise at 10ns, stay high
    ckt.PieceWiseLinearVoltageSource(
        name="go", positive="go", negative="0",
        values=[(0, 0), (9.9e-9, 0), (10e-9, VDD), (SIM_TIME, VDD)])

    # ADC done: modeled as adc_go buffered through RC delay (~8ns SAR time)
    wn, ln = _pdk.sizing["inv_n"]
    wp, lp = _pdk.sizing["inv_p"]
    ckt.raw_spice("Radc_model adc_go adc_dly 5k")
    ckt.raw_spice("Cadc_model adc_dly 0 1.6p")
    ckt.raw_spice(f"Xinv_ad1_n adc_buf_b adc_dly 0 0 {_pdk.nfet} W={wn} L={ln}")
    ckt.raw_spice(f"Xinv_ad1_p adc_buf_b adc_dly vdd vdd {_pdk.pfet} W={wp} L={lp}")
    ckt.raw_spice(f"Xinv_ad2_n adc_done adc_buf_b 0 0 {_pdk.nfet} W={wn} L={ln}")
    ckt.raw_spice(f"Xinv_ad2_p adc_done adc_buf_b vdd vdd {_pdk.pfet} W={wp} L={lp}")

    # Instantiate controller
    ckt.raw_spice("Xctrl go adc_done xbar_rst adc_go latch_out done vdd 0 async_ctrl")

    sim = ckt.simulator(simulator=BACKEND)
    result = sim.transient(step_time=0.1e-9, end_time=SIM_TIME)
    n = len(result.time)

    vth = VDD / 2
    signals = {}
    for name in ["go", "xbar_rst", "adc_go", "adc_done", "latch_out", "done"]:
        try:
            signals[name] = list(result[name])
        except KeyError:
            print(f"  WARNING: signal '{name}' not found")
            signals[name] = [0.0] * n

    # Find rising edges
    edges = {}
    for name in ["go", "xbar_rst", "adc_go", "adc_done", "latch_out", "done"]:
        edges[name] = find_threshold_crossing(signals[name], vth, "rising")

    rst_fall = find_threshold_crossing(signals["xbar_rst"], vth, "falling")

    print(f"\n  Signal transitions (rising edge index):")
    for name, idx in edges.items():
        pct = f"{idx / n * 100:.1f}%" if idx else "N/A"
        print(f"    {name:12s}: index {idx if idx else 'N/A':>6}  ({pct})")
    if rst_fall:
        print(f"    {'xbar_rst_f':12s}: index {rst_fall:>6}  ({rst_fall / n * 100:.1f}%)")

    # Verify correct ordering
    print(f"\n  Sequence check:")
    checks = [
        ("GO -> xbar_rst rise", edges.get("go"), edges.get("xbar_rst")),
        ("xbar_rst rise -> fall (reset phase)", edges.get("xbar_rst"), rst_fall),
        ("xbar_rst fall -> adc_go (settle phase)", rst_fall, edges.get("adc_go")),
        ("adc_go -> done (ADC phase)", edges.get("adc_go"), edges.get("done")),
    ]

    all_pass = True
    for label, t1, t2 in checks:
        if t1 is not None and t2 is not None:
            ok = t1 <= t2
            if not ok:
                all_pass = False
            gap = t2 - t1
            print(f"    {label:40s} gap={gap:>5}  {'PASS' if ok else 'FAIL'}")
        else:
            print(f"    {label:40s} MISSING EDGE")
            all_pass = False

    # Verify done asserted at end
    done_final = signals["done"][-1] > vth
    print_result("\n    Done asserted at end", done_final)
    all_pass &= done_final

    print(f"\n{'='*60}")
    print(f"  OVERALL: {'PASS' if all_pass else 'FAIL'}")
    print(f"{'='*60}\n")
    return all_pass


if __name__ == "__main__":
    run_timing_test()
