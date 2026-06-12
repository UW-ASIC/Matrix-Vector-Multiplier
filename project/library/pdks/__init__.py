"""PDK abstraction layer.

Usage:
    from library.pdks import get_pdk
    pdk = get_pdk()

    # Access sizing
    w, l = pdk.sizing["comp_input"]

    # Generate MOSFET lines
    pdk.mos("m1", "d", "g", "s", "b", pdk.nfet, W=w, L=l)

    # Include models in testbench
    pdk.include_models(circuit, corner="tt", temp=27)
"""

from .base import ACTIVE_PDK, PDKConfig
from .sky130 import Sky130
from .gf180mcu import GF180MCU
from .ihp_sg13g2 import IHP_SG13G2

_REGISTRY = {
    "sky130": Sky130,
    "gf180mcu": GF180MCU,
    "ihp-sg13g2": IHP_SG13G2,
}

_instance = None


def get_pdk() -> PDKConfig:
    """Return the active PDK configuration singleton."""
    global _instance
    from .base import ACTIVE_PDK as _current
    if _instance is None or _instance.name != _current:
        cls = _REGISTRY.get(_current)
        if cls is None:
            raise ValueError(
                f"Unknown PDK '{_current}'. Available: {list(_REGISTRY.keys())}"
            )
        _instance = cls()
    return _instance
