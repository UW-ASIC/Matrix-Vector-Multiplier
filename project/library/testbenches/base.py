"""Shared test harness utilities."""
import argparse
import re

from library.pdks import get_pdk

BACKEND = "ngspice"


def parse_rigor(defaults: dict) -> dict:
    """Parse CLI args for rigor configuration."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--corner", default=",".join(defaults["corners"]))
    parser.add_argument("--temp", default=",".join(map(str, defaults["temps"])))
    parser.add_argument("--mc", type=int, default=defaults["monte_carlo"])
    parser.add_argument("--backend", default=defaults["backend"])
    args = parser.parse_args()
    return {
        "corners": args.corner.split(","),
        "temps": [int(t) for t in args.temp.split(",")],
        "monte_carlo": args.mc,
        "backend": args.backend,
    }


def select_backend(analysis_type: str, rigor: dict) -> str:
    """Select simulation backend based on analysis requirements."""
    if rigor.get("monte_carlo", 0) > 0:
        return "xyce"
    if analysis_type == "fft":
        return "xyce"
    return "vacask"


def validate_ports(spice_text: str, subckt_name: str, required_ports: list) -> None:
    """Check DUT has required ports. Raise if mismatch."""
    pattern = rf"\.subckt\s+{re.escape(subckt_name)}\s+(.+)"
    match = re.search(pattern, spice_text, re.IGNORECASE)
    if not match:
        raise ValueError(f"Subcircuit '{subckt_name}' not found in SPICE text")
    ports = match.group(1).split()
    missing = [p for p in required_ports if p not in ports]
    if missing:
        raise ValueError(f"DUT '{subckt_name}' missing required ports: {missing}")


def fix_xlines(spice_text: str) -> str:
    """No-op: components now generate ngspice-format X-lines directly."""
    return spice_text


def print_header(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_result(label: str, passed: bool) -> None:
    status = "PASS" if passed else "FAIL"
    print(f"  {label}: {status}")


def find_threshold_crossing(data, threshold, direction="rising"):
    """Find first index where signal crosses threshold."""
    for i in range(1, len(data)):
        if direction == "rising" and data[i - 1] < threshold <= data[i]:
            return i
        if direction == "falling" and data[i - 1] > threshold >= data[i]:
            return i
    return None


def pwl_spice(name: str, pos: str, neg: str, values: list) -> str:
    """Generate a raw SPICE PWL voltage source line."""
    pairs = " ".join(f"{t} {v}" for t, v in values)
    return f"V{name} {pos} {neg} PWL({pairs})"


def make_circuit(name: str, vdd: float = None, corner: str = None, temp: int = 27):
    """Create a Circuit with active PDK models.

    Uses proper API methods — no raw_spice for options/temp/supply.
    Backend-agnostic: works with ngspice, vacask, xyce.
    """
    from pyspice_rs import Circuit
    pdk = get_pdk()
    if vdd is None:
        vdd = pdk.vdd
    if corner is None:
        corner = pdk.corners[0]
    ckt = Circuit(name)
    pdk.include_models(ckt, corner=corner, temp=temp)
    ckt.options(scale="1e-6", reltol="5e-3", abstol="1e-10",
                vntol="1e-4", method="gear", itl1="300", itl4="500")
    ckt.V(name="dd", positive="vdd", negative="0", value=vdd)
    return ckt


def make_circuit_mc(name: str, vdd: float = None, temp: int = 27, seed: int = 0,
                    corner: str = None):
    """Create a Circuit with active PDK Monte Carlo models."""
    from pyspice_rs import Circuit
    pdk = get_pdk()
    if vdd is None:
        vdd = pdk.vdd
    if corner is None:
        corner = pdk.corners[0]
    ckt = Circuit(name)
    pdk.include_models_mc(ckt, corner=corner, temp=temp, seed=seed)
    ckt.options(scale="1e-6", reltol="5e-3", abstol="1e-10",
                vntol="1e-4", method="gear", itl1="300", itl4="500")
    ckt.V(name="dd", positive="vdd", negative="0", value=vdd)
    return ckt
