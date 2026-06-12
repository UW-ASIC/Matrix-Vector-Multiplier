"""Sky130 PDK configuration and sizing.

All sizing derived from Gm/ID methodology — see CALCULATIONS.md.
Node: 130nm (drawn 150nm min L), VDD=1.8V.
"""

import os
from pathlib import Path
from .base import PDKConfig


def _get_pdk_root() -> Path:
    env = os.environ.get("PDK_ROOT")
    if env:
        p = Path(env)
        if p.is_dir():
            return p
    fallback = Path.home() / ".ciel"
    if fallback.is_dir():
        return fallback
    raise FileNotFoundError(
        "PDK_ROOT not found. Set PDK_ROOT env var or install via Ciel (~/.ciel)."
    )


def _lib_path() -> Path:
    return _get_pdk_root() / "sky130A" / "libs.tech" / "ngspice" / "sky130.lib.spice"


class Sky130(PDKConfig):
    def __init__(self):
        super().__init__(
            name="sky130",
            vdd=1.8,
            min_l=0.15,
            nfet="sky130_fd_pr__nfet_01v8",
            pfet="sky130_fd_pr__pfet_01v8",
            nfet_lvt="sky130_fd_pr__nfet_01v8_lvt",
            pfet_hvt="sky130_fd_pr__pfet_01v8_hvt",
            un_cox=270.0,   # uA/V^2
            up_cox=90.0,
            vth_n=0.36,
            vth_p=0.36,
            corners=("tt", "ss", "ff", "sf", "fs"),

            # ── Sizing (W, L) in microns ──
            # From CALCULATIONS.md Gm/ID methodology
            sizing={
                # Inverter (min-size, 2:1 P:N for equal rise/fall)
                "inv_n": ("0.42", "0.15"),
                "inv_p": ("0.84", "0.15"),

                # StrongARM comparator
                "comp_input": ("7.0", "0.15"),      # gm/ID=13, moderate inversion
                "comp_latch_n": ("1.0", "0.15"),    # gm/ID~8, strong inversion
                "comp_latch_p": ("4.5", "0.15"),    # match NMOS gm (un/up~3)
                "comp_tail": ("0.42", "0.15"),      # min-size, VGS=VDD
                "comp_reset": ("1.0", "0.15"),      # precharge <0.5ns

                # Charge DAC switch (Ron<500 ohm at ss/-40C)
                "dac_sw_n": ("1.68", "0.15"),
                "dac_sw_p": ("3.36", "0.15"),

                # Sample-hold switch (low Qinj, Ron~1.2k ok)
                "sh_sw_n": ("0.84", "0.15"),
                "sh_sw_p": ("1.68", "0.15"),

                # IMC crossbar reset (500fF in <2ns)
                "xbar_rst_n": ("1.26", "0.15"),
                "xbar_rst_p": ("7.0", "0.15"),

                # IMC crosspoint cap array switch
                "xbar_xpt_n": ("1.26", "0.15"),
                "xbar_xpt_p": ("2.52", "0.15"),

                # ADC mux switch (minimal parasitic)
                "adc_mux_n": ("0.42", "0.15"),
                "adc_mux_p": ("1.42", "0.15"),

                # Async controller Muller C-element
                "muller_p_series": ("1.0", "0.15"),
                "muller_n_series": ("0.5", "0.15"),
                "muller_keeper_p": ("0.5", "0.15"),
                "muller_keeper_n": ("0.25", "0.15"),
                "muller_fb_p": ("0.25", "0.30"),
                "muller_fb_n": ("0.15", "0.30"),
            },

            # ── Capacitors ──
            caps={
                "c_unit": 50e-15,       # unit cap (DAC + crossbar)
                "c_int": 500e-15,       # integration cap
                "c_hold": 200e-15,      # sample-hold
                "c_load_delay": 220e-15,  # delay chain load
            },

            # ── Delay chain ──
            delay={
                "n_rst_stages": 10,     # ~5ns reset phase
                "n_settle_stages": 20,  # ~10ns settle phase
                "cload": "220f",
            },
        )

    def include_models(self, circuit, corner: str = "tt", temp: int = 27):
        if corner not in self.corners:
            raise ValueError(f"Invalid corner '{corner}', must be one of {self.corners}")
        circuit.lib(str(_lib_path()), corner)
        circuit.temp(temp)

    def include_models_mc(self, circuit, corner: str = "tt", temp: int = 27,
                          seed: int = 0):
        if corner not in self.corners:
            raise ValueError(f"Invalid corner '{corner}', must be one of {self.corners}")
        circuit.lib(str(_lib_path()), f"{corner}_mm")
        circuit.temp(temp)
