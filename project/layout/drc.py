"""Sky130 minimum design rules.

All dimensions in microns. These are the minimum values from the Sky130 DRM
needed for layout generators to produce DRC-clean geometry.
"""


class DRC:
    """Sky130 design-rule constants (microns)."""

    # --- Poly ---
    POLY_W = 0.15
    POLY_SP = 0.21
    POLY_EXT_DIFF = 0.13
    POLY_EXT_DIFF_PMOS = 0.25  # poly.7: PMOS poly endcap >= 0.25
    POLY_ENDCAP = 0.13

    # --- Diffusion ---
    DIFF_W = 0.15
    DIFF_SP = 0.27
    DIFF_ENCL_LICON = 0.04
    DIFF_CHANNEL_W = 0.42

    # --- Tap ---
    TAP_W = 0.29
    PTAP_ENCL_LICON = 0.12   # licon.7: P-tap enclosure of LICON >= 0.12

    # --- N-well ---
    NWELL_W = 0.84
    NWELL_SP = 1.27
    NWELL_ENCL_DIFF = 0.18
    NWELL_ENCL_TAP = 0.18
    NDIFF_SP_NWELL = 0.34       # diff/tap.9: N-diffusion spacing to N-well

    # --- NPC (nitride poly cut) ---
    NPC_W = 0.27
    NPC_SP = 0.27
    NPC_ENCL_LICON = 0.05

    # --- LICON (local interconnect contact) ---
    LICON_SZ = 0.17
    LICON_SP = 0.17

    # --- LI1 (local interconnect) ---
    LI1_W = 0.17
    LI1_SP = 0.17
    LI1_ENCL_LICON = 0.08

    # --- MCON (metal contact) ---
    MCON_SZ = 0.17
    MCON_SP = 0.19
    MCON_ENCL_MET1 = 0.03
    MCON_ENCL_MET1_WIDE = 0.06

    # --- MET1 ---
    MET1_W = 0.14
    MET1_SP = 0.14
    MET1_AREA = 0.083

    # --- VIA ---
    VIA_SZ = 0.15
    VIA_SP = 0.17
    VIA_ENCL_MET1 = 0.055
    VIA_ENCL_MET2 = 0.055

    # --- MET2 ---
    MET2_W = 0.14
    MET2_SP = 0.14
    MET2_AREA = 0.0676

    # --- VIA2 ---
    VIA2_SZ = 0.20
    VIA2_SP = 0.20
    VIA2_ENCL_MET2 = 0.04
    VIA2_ENCL_MET3 = 0.065

    # --- MET3 ---
    MET3_W = 0.30
    MET3_SP = 0.30

    # --- VIA3 ---
    VIA3_SZ = 0.20
    VIA3_SP = 0.20
    VIA3_ENCL_MET3 = 0.06
    VIA3_ENCL_MET4 = 0.065

    # --- MET4 ---
    MET4_W = 0.30
    MET4_SP = 0.30

    # --- VIA4 ---
    VIA4_SZ = 0.80
    VIA4_SP = 0.80
    VIA4_ENCL_MET4 = 0.19
    VIA4_ENCL_MET5 = 0.31

    # --- MET5 ---
    MET5_W = 1.60
    MET5_SP = 1.60

    # --- Implants ---
    NSDM_ENCL = 0.125
    PSDM_ENCL = 0.125

    # --- CAPM (MIM capacitor) ---
    CAPM_W = 1.0
    CAPM_SP = 0.84
    CAPM_ENCL_MET3 = 0.14
    CAPM_SP_VIA3 = 0.08
    CAPM_SP_VIA2 = 0.10
    CAPM_SP_UNREL_MET3 = 1.34

    # --- Parasitic capacitance ---
    MIM_AREA_CAP = 2.0    # fF/um^2
    MIM_PERI_CAP = 0.19   # fF/um
