# MVM Testing Infrastructure

## Overview

All components are tested with real **sky130 PDK** models (BSIM4 binned subcircuits via `.lib`) — no ideal/level-1 models anywhere. Tests run across full PVT (Process-Voltage-Temperature) conditions.

## Running Tests

```bash
nix develop
cd project
export PYTHONPATH=.

# Single component, default rigor (tt/27C)
python testbenches/tb_strongarm.py

# Full PVT sweep
python testbenches/tb_strongarm.py --corner tt,ss,ff --temp=-40,27,125

# Top-level with PVT + mismatch
python testbenches/top/tb_gemm_tapeout.py --corner tt,ss,ff --temp=-40,27,125 --mc 10

# Run all
for tb in testbenches/tb_*.py; do python "$tb" --corner tt,ss,ff --temp=-40,27,125; done
python testbenches/top/tb_gemm_tapeout.py --corner tt,ss,ff --temp=-40,27,125 --mc 10
```

## CLI Arguments

| Flag | Default | Description |
|------|---------|-------------|
| `--corner` | `tt` | Comma-separated corners: `tt,ss,ff,sf,fs` |
| `--temp` | `27` | Comma-separated temps (use `=` for negatives): `--temp=-40,27,125` |
| `--mc` | `0` | Number of mismatch runs (uses `tt_mm` corner) |
| `--backend` | `ngspice` | Simulation backend |

## Test Matrix (Verified Passing)

| Testbench | Conditions | Checks | Result |
|-----------|-----------|--------|--------|
| `tb_strongarm.py` | 9 PVT | offset, delay, power | PASS |
| `tb_charge_dac.py` | 9 PVT | DNL/INL, monotonicity, settling | PASS |
| `tb_sample_hold_bank.py` | 9 PVT | acquisition, droop, charge injection | PASS |
| `tb_imc_crossbar.py` | 9 PVT | R^2 linearity, SNR, crosstalk | PASS |
| `tb_interleaved_adc.py` | 9 PVT | sweep, monotonicity, missing codes | PASS |
| `tb_gemm_tapeout.py` | 9 PVT + 10 MC | 184 checks, 4 vectors × 4 cols | PASS |

## Architecture

```
project/
├── library/testbenches/
│   ├── base.py              # make_circuit(), parse_rigor(), pwl_spice(), etc.
│   ├── tb_comparator.py     # Comparator harness (offset, delay, power)
│   ├── tb_dac.py            # DAC harness (DNL/INL, monotonicity, settling)
│   ├── tb_adc.py            # ADC harness (sweep, missing codes, latency)
│   ├── tb_sample_hold.py    # S&H harness (acquisition, droop, charge injection)
│   └── tb_imc.py            # IMC harness (MAC linearity, SNR, crosstalk)
├── testbenches/
│   ├── tb_strongarm.py      # Thin wrapper → tb_comparator.run()
│   ├── tb_charge_dac.py     # Thin wrapper → tb_dac.run()
│   ├── tb_sample_hold_bank.py
│   ├── tb_imc_crossbar.py
│   ├── tb_interleaved_adc.py
│   └── top/
│       ├── generate_stimulus.py   # Random weights/inputs + physics-based expected codes
│       └── tb_gemm_tapeout.py     # Full system: crossbar + ADC, multi-vector PVT
```

### Pattern

Component testbenches are one-liners that delegate to library harnesses:

```python
from components.strongarm.strongarm import generate
from library.testbenches.tb_comparator import run

if __name__ == "__main__":
    run(generate, "strongarm")
```

The harness handles PVT loop, circuit construction, measurement, and pass/fail.

## Key Technical Details

### Sky130 Models
- Models are **subcircuits** (not `.model`) — MOSFETs use X-lines
- `.option scale=1e-6` — W/L values in microns without `u` suffix
- `.lib sky130.lib.spice <corner>` loaded via `ckt.lib()` for correct placement

### Backends
- **ngspice** (batch): Primary backend, works reliably
- **Xyce 7.10.0**: Available in shell for future `.SAMPLING` MC
- **vacask**: Has branch-current read issues, not used for tests

### Monte Carlo
- Sky130's `$rdist_*` functions are HSPICE-only (incompatible with ngspice)
- Current MC uses `tt_mm` corner (mismatch flags enabled) across multiple runs
- For true statistical MC, use Xyce with `.SAMPLING` directive

### Charge-Domain Circuits
- Crossbar inputs MUST step AFTER reset drops (charge injection timing)
- DAC bits must step (not DC) for charge redistribution to work
- Cap array `cap_bot` nodes need 100G bias resistors for DC operating point
- Expected voltages use physics model: `V = C_ON * Vref / (C_ON + C_OFF + C_load)`

## Pass Criteria

| Component | Metric | Spec |
|-----------|--------|------|
| Comparator | Offset | < 10 mV |
| Comparator | Propagation delay | < 3 ns |
| DAC | DNL | < 1 LSB |
| DAC | INL | < 1 LSB |
| DAC | Settling time | < 15 ns |
| Sample-Hold | Acquisition error | < 50 mV |
| Sample-Hold | Droop rate | < 1 mV/ns |
| Sample-Hold | Charge injection | < 30 mV |
| IMC Crossbar | MAC linearity R^2 | > 0.95 |
| IMC Crossbar | Compute SNR | > 30 dB |
| IMC Crossbar | Crosstalk | < 10 mV |
| ADC | Monotonicity | Required |
| ADC | Missing codes | None |
| Top-level | ADC code accuracy | +/- 1 LSB |
