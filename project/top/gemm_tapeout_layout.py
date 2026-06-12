"""Top-level GEMM tapeout layout — floorplan with block placement."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.strongarm.strongarm_layout import layout as strongarm_layout
from components.charge_dac.charge_dac_layout import layout as charge_dac_layout
from components.sample_hold_bank.sample_hold_bank_layout import layout as sh_layout
from components.imc_crossbar.imc_crossbar_layout import layout as crossbar_layout
from components.interleaved_adc.interleaved_adc_layout import layout as adc_layout
from components.async_ctrl.async_ctrl_layout import layout as ctrl_layout


def layout_all():
    """Build and export all component layouts."""
    print("=== GEMM Tapeout Layout ===\n")

    results = {}
    blocks = [
        ("strongarm", strongarm_layout),
        ("charge_dac", charge_dac_layout),
        ("sample_hold_bank", sh_layout),
        ("imc_crossbar", crossbar_layout),
        ("interleaved_adc", adc_layout),
        ("async_ctrl", ctrl_layout),
    ]

    for name, fn in blocks:
        print(f"--- {name} ---")
        try:
            comp = fn()
            results[name] = {"status": "pass", "state": comp.state()}
        except Exception as e:
            results[name] = {"status": "fail", "error": str(e)}
            print(f"  FAILED: {e}")
        print()

    # Summary
    print("=== Summary ===")
    for name, r in results.items():
        if r["status"] == "pass":
            print(f"  {name:25s} PASS  state={r['state']}")
        else:
            print(f"  {name:25s} FAIL  {r['error'][:60]}")

    return results


if __name__ == "__main__":
    layout_all()
