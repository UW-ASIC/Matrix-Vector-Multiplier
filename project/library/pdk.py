"""PDK interface — delegates to library.pdks.

All components and testbenches import from here.
"""

from library.pdks import get_pdk

_pdk = get_pdk()

# Model names
NFET = _pdk.nfet
PFET = _pdk.pfet
NFET_LVT = _pdk.nfet_lvt
PFET_HVT = _pdk.pfet_hvt
VDD = _pdk.vdd

# Gate helpers
mos = _pdk.mos
inv = _pdk.inv
nand2 = _pdk.nand2
nor2 = _pdk.nor2

# Model inclusion
include_models = _pdk.include_models
include_models_mc = _pdk.include_models_mc
