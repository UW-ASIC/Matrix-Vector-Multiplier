"""IHP SG13G2 PDK configuration and sizing.

IHP 130nm SiGe BiCMOS process — available via ciel.
Similar node to sky130 but with SiGe HBTs and better analog performance.
VDD = 1.2V (for CMOS logic), analog can use 1.5V or higher.
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


class IHP_SG13G2(PDKConfig):
    """IHP SG13G2 130nm SiGe BiCMOS.

    Using 1.2V CMOS devices (sg13_lv_nmos/pmos).
    """

    def __init__(self):
        super().__init__(
            name="ihp-sg13g2",
            vdd=1.2,
            min_l=0.13,
            nfet="sg13_lv_nmos",
            pfet="sg13_lv_pmos",
            nfet_lvt="sg13_lv_nmos",
            pfet_hvt="sg13_lv_pmos",
            un_cox=350.0,   # uA/V^2 (thinner oxide than sky130)
            up_cox=120.0,
            vth_n=0.35,
            vth_p=0.38,
            corners=("typ", "slow", "fast"),

            # ── Sizing (W, L) in microns ──
            # VDD=1.2V, min_L=0.13um. Higher un_cox than sky130 → smaller W.
            sizing={
                "inv_n": ("0.39", "0.13"),
                "inv_p": ("0.78", "0.13"),

                "comp_input": ("5.0", "0.13"),
                "comp_latch_n": ("0.78", "0.13"),
                "comp_latch_p": ("2.34", "0.13"),
                "comp_tail": ("0.39", "0.13"),
                "comp_reset": ("0.78", "0.13"),

                "dac_sw_n": ("1.3", "0.13"),
                "dac_sw_p": ("2.6", "0.13"),

                "sh_sw_n": ("0.65", "0.13"),
                "sh_sw_p": ("1.3", "0.13"),

                "xbar_rst_n": ("1.0", "0.13"),
                "xbar_rst_p": ("5.0", "0.13"),

                "xbar_xpt_n": ("1.0", "0.13"),
                "xbar_xpt_p": ("2.0", "0.13"),

                "adc_mux_n": ("0.39", "0.13"),
                "adc_mux_p": ("1.17", "0.13"),

                "muller_p_series": ("0.78", "0.13"),
                "muller_n_series": ("0.39", "0.13"),
                "muller_keeper_p": ("0.39", "0.13"),
                "muller_keeper_n": ("0.26", "0.13"),
                "muller_fb_p": ("0.26", "0.26"),
                "muller_fb_n": ("0.13", "0.26"),
            },

            caps={
                "c_unit": 30e-15,       # slightly smaller (VDD=1.2V, SNR ok)
                "c_int": 300e-15,
                "c_hold": 150e-15,
                "c_load_delay": 150e-15,
            },

            delay={
                "n_rst_stages": 10,
                "n_settle_stages": 18,
                "cload": "150f",
            },
        )

    def include_models(self, circuit, corner: str = "typ", temp: int = 27):
        if corner not in self.corners:
            raise ValueError(f"Invalid corner '{corner}', must be one of {self.corners}")
        pdk = _get_pdk_root()
        lib_path = pdk / "ihp-sg13g2" / "libs.tech" / "ngspice" / "sg13g2.lib.spice"
        circuit.lib(str(lib_path), corner)
        circuit.temp(temp)

    def include_models_mc(self, circuit, corner: str = "typ", temp: int = 27,
                          seed: int = 0):
        self.include_models(circuit, corner, temp)
