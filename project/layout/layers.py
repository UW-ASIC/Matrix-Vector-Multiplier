"""Sky130 GDS layer/datatype mapping.

Every attribute is a (layer, datatype) tuple suitable for gdstk calls.
Use ld(LAYER) to unpack into {"layer": ..., "datatype": ...} kwargs.
"""


class L:
    """Sky130 layer definitions as (GDS layer, datatype) pairs."""

    # --- Wells ---
    NWELL = (64, 20)
    DNWELL = (64, 18)

    # --- Diffusion & Tap ---
    DIFF = (65, 20)
    TAP = (65, 44)

    # --- Poly ---
    POLY = (66, 20)

    # --- Contacts ---
    LICON = (66, 44)
    NPC = (95, 20)

    # --- Implants ---
    NSDM = (93, 44)
    PSDM = (94, 20)
    HVTP = (78, 44)
    LVTN = (125, 44)
    HVI = (75, 20)

    # --- Local Interconnect ---
    LI1 = (67, 20)
    MCON = (67, 44)

    # --- Metal stack ---
    MET1 = (68, 20)
    VIA = (68, 44)
    MET2 = (69, 20)
    VIA2 = (69, 44)
    MET3 = (70, 20)
    VIA3 = (70, 44)
    MET4 = (71, 20)
    VIA4 = (71, 44)
    MET5 = (72, 20)

    # --- Special ---
    CAPM = (89, 44)
    CAP2M = (97, 44)
    PAD = (76, 20)

    # --- Pin layers (datatype 16) ---
    LI1_PIN = (67, 16)
    MET1_PIN = (68, 16)
    MET2_PIN = (69, 16)
    MET3_PIN = (70, 16)
    MET4_PIN = (71, 16)
    MET5_PIN = (72, 16)

    # --- Label layers (datatype 5) ---
    LI1_LBL = (67, 5)
    MET1_LBL = (68, 5)
    MET2_LBL = (69, 5)
    MET3_LBL = (70, 5)
    MET4_LBL = (71, 5)
    MET5_LBL = (72, 5)

    # --- Convenience lists (ordered LI1 through MET5) ---
    METALS = [
        (67, 20),   # LI1
        (68, 20),   # MET1
        (69, 20),   # MET2
        (70, 20),   # MET3
        (71, 20),   # MET4
        (72, 20),   # MET5
    ]

    VIAS = [
        (66, 44),   # LICON
        (67, 44),   # MCON
        (68, 44),   # VIA
        (69, 44),   # VIA2
        (70, 44),   # VIA3
        (71, 44),   # VIA4
    ]

    PINS = [
        (67, 16),   # LI1_PIN
        (68, 16),   # MET1_PIN
        (69, 16),   # MET2_PIN
        (70, 16),   # MET3_PIN
        (71, 16),   # MET4_PIN
        (72, 16),   # MET5_PIN
    ]

    LABELS = [
        (67, 5),    # LI1_LBL
        (68, 5),    # MET1_LBL
        (69, 5),    # MET2_LBL
        (70, 5),    # MET3_LBL
        (71, 5),    # MET4_LBL
        (72, 5),    # MET5_LBL
    ]


def ld(layer: tuple[int, int]) -> dict:
    """Unpack a (layer, datatype) tuple into gdstk keyword arguments.

    Usage: gdstk.rectangle(p1, p2, **ld(L.MET1))
    """
    return {"layer": layer[0], "datatype": layer[1]}
