"""MIM capacitor layout generators for Sky130.

Sky130 MIM capacitors use the CAPM layer over MET3:
    - Bottom plate = MET3 (drawing layer)
    - Top plate = CAPM (capacitor marker layer)
    - Top plate connection via VIA3 to MET4
    - Bottom plate connection on MET3

Capacitance model:
    C = MIM_AREA_CAP * W * H + MIM_PERI_CAP * 2 * (W + H)
    where MIM_AREA_CAP = 2.0 fF/um^2, MIM_PERI_CAP = 0.19 fF/um
"""

import math
import gdstk
from ..layers import L, ld
from ..drc import DRC
from ..ports import Port
from .contact import via_array


def mim_cap(lib: gdstk.Library, w: float, h: float,
            name: str | None = None) -> tuple[gdstk.Cell, dict[str, Port]]:
    """Generate a MIM capacitor cell.

    Bottom plate = MET3, top plate = CAPM connected via VIA3 to MET4.
    Cell origin at geometric center.

    Args:
        lib:  gdstk Library.
        w:    Capacitor width in microns (must be >= CAPM_W = 1.0).
        h:    Capacitor height in microns (must be >= CAPM_W = 1.0).
        name: Cell name. Auto-generated if None.

    Returns:
        (cell, ports) with ports "TOP" (met4, north) and "BOT" (met3, south).
    """
    if name is None:
        w_nm = round(w * 1000)
        h_nm = round(h * 1000)
        name = f"sky130_mimcap_{w_nm}x{h_nm}"

    cell = lib.new_cell(name)

    hw = w / 2
    hh = h / 2

    # --- Bottom plate: MET3 ---
    # MET3 must extend beyond CAPM by CAPM_ENCL_MET3
    m3_encl = DRC.CAPM_ENCL_MET3
    cell.add(gdstk.rectangle(
        (-hw - m3_encl, -hh - m3_encl),
        (hw + m3_encl, hh + m3_encl),
        **ld(L.MET3),
    ))

    # --- Top plate: CAPM ---
    cell.add(gdstk.rectangle((-hw, -hh), (hw, hh), **ld(L.CAPM)))

    # --- VIA3 array on top plate (connecting CAPM to MET4) ---
    # capm.4: CAPM must enclose VIA3 (MIM cap contact) by >= 0.08 um.
    # capm.8: CAPM must be spaced from VIA2 by >= 0.10 um.
    # Use max(CAPM_SP_VIA3, CAPM_SP_VIA2) + 0.02 margin to satisfy both
    # rules and avoid marginal-tolerance DRC failures.
    via3_margin = max(DRC.CAPM_SP_VIA3, DRC.CAPM_SP_VIA2) + 0.02  # 0.12 um
    via3_x0 = -hw + via3_margin
    via3_y0 = -hh + via3_margin
    via3_x1 = hw - via3_margin
    via3_y1 = hh - via3_margin
    via_array(cell, L.VIA3, via3_x0, via3_y0, via3_x1, via3_y1,
              DRC.VIA3_SZ, DRC.VIA3_SP)

    # --- MET4 landing pad over VIA3 ---
    m4_encl = DRC.VIA3_ENCL_MET4
    cell.add(gdstk.rectangle(
        (via3_x0 - m4_encl, via3_y0 - m4_encl),
        (via3_x1 + DRC.VIA3_SZ + m4_encl, via3_y1 + DRC.VIA3_SZ + m4_encl),
        **ld(L.MET4),
    ))

    # --- Ports ---
    # TOP port: center of MET4 at north edge
    top_y = hh + m3_encl
    bot_y = -hh - m3_encl
    port_w = min(w, 0.50)  # reasonable port width

    ports = {
        "TOP": Port("TOP", (0.0, top_y), port_w, 90.0, L.MET4),
        "BOT": Port("BOT", (0.0, bot_y), port_w, 270.0, L.MET3),
    }

    return cell, ports


def unit_cap(lib: gdstk.Library, target_fF: float,
             name: str | None = None) -> tuple[gdstk.Cell, dict[str, Port]]:
    """Generate a square MIM unit capacitor sized for a target capacitance.

    Solves for the square side length s such that:
        C = MIM_AREA_CAP * s^2 + MIM_PERI_CAP * 4 * s = target_fF

    This is a quadratic in s:
        MIM_AREA_CAP * s^2 + 4 * MIM_PERI_CAP * s - target_fF = 0

    The side length is clamped to a minimum of CAPM_W (1.0 um).

    Args:
        lib:       gdstk Library.
        target_fF: Target capacitance in femtofarads.
        name:      Cell name. Auto-generated if None.

    Returns:
        (cell, ports) -- same as mim_cap().
    """
    a = DRC.MIM_AREA_CAP       # 2.0 fF/um^2
    b = 4 * DRC.MIM_PERI_CAP   # 4 * 0.19 = 0.76 fF/um
    c = -target_fF

    # Quadratic formula: s = (-b + sqrt(b^2 - 4ac)) / (2a)
    discriminant = b * b - 4 * a * c
    if discriminant < 0:
        raise ValueError(f"Cannot achieve {target_fF} fF with MIM cap (negative discriminant)")

    s = (-b + math.sqrt(discriminant)) / (2 * a)
    s = max(s, DRC.CAPM_W)  # enforce minimum dimension

    # Round to nearest 10nm for clean GDS
    s = math.ceil(s * 100) / 100

    if name is None:
        name = f"sky130_unit_cap_{round(target_fF * 1000)}aF"

    return mim_cap(lib, s, s, name=name)
