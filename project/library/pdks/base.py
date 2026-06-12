"""PDK configuration base class and active PDK selector."""

from dataclasses import dataclass, field


# ──────────────────────────────────────────────────────────────
# CHANGE THIS TO SWITCH PDK
# ──────────────────────────────────────────────────────────────
ACTIVE_PDK = "sky130"
# ACTIVE_PDK = "gf180mcu"
# ACTIVE_PDK = "ihp-sg13g2"


@dataclass
class PDKConfig:
    """Technology-agnostic PDK descriptor."""

    name: str
    vdd: float
    min_l: float          # minimum drawn length (microns)
    nfet: str             # NFET model/subckt name
    pfet: str             # PFET model/subckt name
    nfet_lvt: str = ""    # low-Vt NFET (optional)
    pfet_hvt: str = ""    # high-Vt PFET (optional)

    # Physical constants for this node
    un_cox: float = 0.0   # mu_n * Cox (uA/V^2) — for Ron calculations
    up_cox: float = 0.0   # mu_p * Cox (uA/V^2)
    vth_n: float = 0.0    # nominal NFET threshold (V)
    vth_p: float = 0.0    # nominal |PFET threshold| (V)

    # Valid corners for this PDK
    corners: tuple = ("tt", "ss", "ff", "sf", "fs")

    # Device sizing — keyed by functional role
    # Each entry: (W, L) in microns
    sizing: dict = field(default_factory=dict)

    # Capacitor values (Farads)
    caps: dict = field(default_factory=dict)

    # Delay chain config
    delay: dict = field(default_factory=dict)

    def mos(self, name, drain, gate, source, bulk, model, **params):
        """Return a MOSFET X-line for this PDK."""
        param_str = " ".join(f"{k}={v}" for k, v in params.items())
        line = f"X{name} {drain} {gate} {source} {bulk} {model}"
        if param_str:
            line += f" {param_str}"
        return line

    def inv(self, prefix, out, inp, vdd, vss, wn=None, ln=None, wp=None, lp=None):
        """Return two X-lines for a CMOS inverter. Defaults to min-size."""
        wn = wn or self.sizing["inv_n"][0]
        ln = ln or self.sizing["inv_n"][1]
        wp = wp or self.sizing["inv_p"][0]
        lp = lp or self.sizing["inv_p"][1]
        return [
            self.mos(f"{prefix}_n", out, inp, vss, vss, self.nfet, W=wn, L=ln),
            self.mos(f"{prefix}_p", out, inp, vdd, vdd, self.pfet, W=wp, L=lp),
        ]

    def nand2(self, prefix, out, a, b, vdd, vss, wn=None, ln=None, wp=None, lp=None):
        """Return X-lines for 2-input NAND."""
        wn = wn or self.sizing["inv_n"][0]
        ln = ln or self.sizing["inv_n"][1]
        wp = wp or self.sizing["inv_p"][0]
        lp = lp or self.sizing["inv_p"][1]
        mid = f"{prefix}_mid"
        return [
            self.mos(f"{prefix}_p1", out, a, vdd, vdd, self.pfet, W=wp, L=lp),
            self.mos(f"{prefix}_p2", out, b, vdd, vdd, self.pfet, W=wp, L=lp),
            self.mos(f"{prefix}_n1", out, a, mid, vss, self.nfet, W=wn, L=ln),
            self.mos(f"{prefix}_n2", mid, b, vss, vss, self.nfet, W=wn, L=ln),
            f"C{prefix}_mid {mid} {vss} 1f",
        ]

    def nor2(self, prefix, out, a, b, vdd, vss, wn=None, ln=None, wp=None, lp=None):
        """Return X-lines for 2-input NOR."""
        wn = wn or self.sizing["inv_n"][0]
        ln = ln or self.sizing["inv_n"][1]
        wp = wp or self.sizing["inv_p"][0]
        lp = lp or self.sizing["inv_p"][1]
        return [
            self.mos(f"{prefix}_p1", out, a, f"{prefix}_mid", vdd, self.pfet, W=wp, L=lp),
            self.mos(f"{prefix}_p2", f"{prefix}_mid", b, vdd, vdd, self.pfet, W=wp, L=lp),
            self.mos(f"{prefix}_n1", out, a, vss, vss, self.nfet, W=wn, L=ln),
            self.mos(f"{prefix}_n2", out, b, vss, vss, self.nfet, W=wn, L=ln),
        ]

    def include_models(self, circuit, corner: str = "tt", temp: int = 27):
        """Add PDK model inclusion to circuit. Override in subclass."""
        raise NotImplementedError(f"include_models not implemented for {self.name}")

    def include_models_mc(self, circuit, corner: str = "tt", temp: int = 27,
                          seed: int = 0):
        """Add Monte Carlo models. Override in subclass."""
        raise NotImplementedError(f"include_models_mc not implemented for {self.name}")
