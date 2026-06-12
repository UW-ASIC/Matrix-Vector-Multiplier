# MVM — Matrix-Vector Multiplier

Analog circuit layout project targeting Sky130 PDK.

## Workflow

Write components as Python files in `project/` using `pyspice_rs`. Each component is a `.subckt`. These files serve two purposes:

1. **Schemify import** — each `.subckt` becomes a `.chn` schematic for visualization and simulation
2. **Spout2 layout** — same netlists feed into Spout2 for automated place-and-route

Convention for writing importable files: **`../Schemify/modules/import/SKILL.md`**

### File categories

| Type | Contains | Schemify result |
|------|----------|-----------------|
| Component | `.subckt` with ports and devices | `.chn` with `stype = schematic` |
| Primitive | `.subckt` with `schemify:primitive` comment | `.chn` with `stype = primitive` |
| Testbench | Top-level with `.tran`/`.ac`/`.dc`/`.op` | `.chn` with `stype = testbench` |

### Hierarchy

Instance `X<name> <subckt_name> ...` → Schemify resolves to `<subckt_name>.chn` by name. Case-sensitive.

## Layout Engine

Uses **Spout2** (`../Spout2/`) Python API directly — NOT Schemify's auto layout engine.

- Full API reference: **`SKILL.md`** in this directory
- Spout2 Python bindings source: `../Spout2/crates/py/src/`
- Spout2 builder/constraint API: `../Spout2/crates/api/src/`
- Constraint IR (24 types): `../Spout2/crates/core/src/constraint.rs`

## Simulation Backend

**PySpice-rs** (`../PySpice/`) — Rust rewrite of PySpice, used by Spout2 for validation and directly for circuit simulation.

- Source: `../PySpice/src/`
- Python module: `pyspice_rs`
- Requires `libngspice` (provided by flake.nix)

## Schematic Editor

**Schemify** (`../Schemify/`) — vim-first analog schematic editor. The flake.nix inherits its dev shell for Zig toolchain, Python, ngspice, and GPU libs. Schemify imports the PySpice `.subckt` files from `project/` as `.chn` schematics.

- Import conventions: `../Schemify/modules/import/SKILL.md`
- Architecture: `../Schemify/CLAUDE.md`

## Dev Environment

`nix develop` provides everything (Schemify env + Rust/maturin for Spout2). On first entry it builds the `spout` Python module from `../Spout2` (which pulls in `../PySpice`) via maturin.

## Project Structure

- `Config.toml` — project config (PDK, paths)
- `flake.nix` — dev shell (inherits Schemify + adds Rust/maturin for Spout2)
- `project/` — component and testbench Python files (pyspice_rs `.subckt` definitions)
- `schematics/` — Schemify `.chn` files (generated from import)
- `testbenches/` — Schemify testbench `.chn` files (generated from import)
