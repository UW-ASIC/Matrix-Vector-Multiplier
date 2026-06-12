# MVM — Charge-Domain In-Memory Computing GEMM Accelerator

4x4 matrix-vector multiplier targeting TinyTapeout on Sky130.
Fully analog compute path, async digital control.

## Architecture

```
Input Vector → [Crossbar (charge-sharing MAC)] → [Interleaved SAR ADC] → Output Codes
                        ↑                                ↑
                   weight caps                     async controller
                   (4-bit binary)                  (self-timed sequencer)
```

## Active Files

### project/components/ (transistor-level subcircuits)
| File | Purpose |
|------|---------|
| `imc_crossbar.py` | 4x4 capacitive crossbar (charge-domain MAC) |
| `interleaved_adc.py` | 2-unit interleaved async SAR ADC (4 columns) |
| `strongarm.py` | 9T StrongARM latch comparator (standalone) |
| `async_ctrl.py` | Self-timed sequencer (delay chains, no clock) |

### project/library/ (reusable building blocks)
| File | Purpose |
|------|---------|
| `pdk.py` | Sky130 include, mos(), inv(), nand2(), nor2() |
| `cap_array.py` | Binary-weighted cap bank with switches |
| `cmos_switch.py` | CMOS transmission gate |

### project/testbenches/ (verified, passing)
| File | Purpose |
|------|---------|
| `tb_gemm_tapeout.py` | Full path: crossbar + ADC, identity weights |
| `tb_interleaved_adc.py` | Standalone ADC: 16 codes, monotonicity, DNL |
| `tb_async_ctrl.py` | Self-timed sequence verification |

### project/sizing/
| File | Purpose |
|------|---------|
| `gm_id_sizing.py` | Gm/Id analysis for all blocks (sky130) |

### project/top/
| File | Purpose |
|------|---------|
| `gemm_tapeout.py` | TinyTapeout top (pins, FSM, behavioral latches) |

### Top-level
| File | Purpose |
|------|---------|
| `CLAUDE.md` | Project conventions for AI assistants |
| `SKILL.md` | Spout2 layout API reference |
| `Config.toml` | Project config (PDK, paths) |
| `flake.nix` | Nix dev shell |
| `pdk_map.json` | Schemify PDK device mapping |
| `project/generate.sh` | Schemify batch import script |

## Deleted (stale/superseded)

### Components (old architecture, replaced by interleaved_adc + imc_crossbar)
- `charge_dac.py` — replaced by direct voltage sources in tapeout flow
- `column_adc.py` — replaced by interleaved_adc.py
- `sample_hold_bank.py` — removed (S&H in gemm_tapeout.py top-level)
- `sar_adc.py` — old single-channel, replaced by interleaved_adc.py
- `tgate_mux.py` — folded into interleaved_adc mux
- `imc_current.py` — comparison study artifact (current-domain)
- `imc_resistive.py` — comparison study artifact (resistive)
- `imc_time.py` — comparison study artifact (time-domain)
- `imc_gemm.py` — early GEMM crossbar prototype, superseded by imc_crossbar.py

### Library (unused)
- `and_gate.py` — not used in any active component
- `cs_amp.py` — not used (no amplifier in charge-domain path)
- `current_mirror.py` — not used (no bias currents in charge-domain)

### Primitives (all behavioral, not used in tapeout flow)
- `ideal_adc.py`, `ideal_dac.py`, `ideal_imc.py`, `ideal_comparator.py`, `ideal_sample_hold.py`

### Testbenches (old components)
- `tb_adc.py` — tests old sar_adc
- `tb_dac.py` — tests old charge_dac
- `tb_imc.py` — tests old imc_crossbar (pre-sizing)
- `tb_mvm.py` — tests old mvm_top
- `tb_gemm.py` — early GEMM test, superseded by tb_gemm_tapeout.py
- `tb_imc_identity.py`, `tb_imc_power.py`, `tb_imc_random.py`, `tb_imc_speed.py`, `tb_imc_sweep.py`, `tb_imc_weight.py` — comparison study artifacts
- `run_imc_comparison.py` — comparison study runner

### Top (old)
- `mvm_top.py` — old DAC→crossbar→S&H→SAR architecture, replaced by gemm_tapeout.py

### Schemify outputs (regenerate via `./project/generate.sh`)
- `components/*.chn` — stale, regenerate after cleanup
- `testbenches/*.chn_tb` — stale
- `top/*.chn` — stale
