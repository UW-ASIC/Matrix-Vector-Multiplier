import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.XSchemInterface import build_and_simulate_variants

# OpAmp variant definitions
VARIANTS = {
    "HighGain": {
        "short": "HG", 
        "params": {
            "M1": {"W": "20", "L": "1"}, 
            "M2": {"W": "20", "L": "1"}, 
            "M3": {"W": "5", "L": "2"}, 
            "M4": {"W": "5", "L": "2"}, 
            "M5": {"W": "40", "L": "0.5"}
        }
    },
    "LowPower": {
        "short": "LP", 
        "params": {
            "M1": {"W": "5", "L": "1"}, 
            "M2": {"W": "5", "L": "1"}, 
            "M3": {"W": "2", "L": "1"}, 
            "M4": {"W": "2", "L": "1"}, 
            "M5": {"W": "10", "L": "1"}
        }
    },
    "HighSpeed": {
        "short": "HS", 
        "params": {
            "M1": {"W": "50", "L": "0.18"}, 
            "M2": {"W": "50", "L": "0.18"}, 
            "M3": {"W": "20", "L": "0.18"}, 
            "M4": {"W": "20", "L": "0.18"}, 
            "M5": {"W": "100", "L": "0.18"}
        }
    },
    "Balanced": {
        "short": "BAL", 
        "params": {
            "M1": {"W": "10", "L": "0.5"}, 
            "M2": {"W": "10", "L": "0.5"}, 
            "M3": {"W": "5", "L": "0.5"}, 
            "M4": {"W": "5", "L": "0.5"}, 
            "M5": {"W": "20", "L": "0.5"}
        }
    }
}

# Test configurations
TESTS = {
    "dc_gain": {
        "v1_common_mode": "DC 0.9V",
        "v3_vplus_input": "DC 0V AC 1V", 
        "v5_vminus_input": "DC 0V",
        "spice": """
.ac dec 100 0.1 1G
.control
run
let dc_gain_val = vdb(vout)[0]
echo 'DC_GAIN:' $&dc_gain_val
let gbw_freq = 0
let i = 0
while i < length(vdb(vout))
  if vdb(vout)[i] <= 0
    let gbw_freq = frequency[i]
    break
  end
  let i = i + 1
end
echo 'GBW:' $&gbw_freq
.endc
"""
    },
    "slew_rate": {
        "v1_common_mode": "DC 0.9V",
        "v3_vplus_input": "PULSE(0 1.8 1u 10n 10n 5u 10u)",
        "v5_vminus_input": "DC 0V",
        "spice": """
.tran 10n 15u
.control
run
let slew_pos = maximum(deriv(v(vout)))
let slew_neg = minimum(deriv(v(vout)))
echo 'SLEW_RATE_POS:' $&slew_pos
echo 'SLEW_RATE_NEG:' $&slew_neg
.endc
"""
    },
    "power_consumption": {
        "v1_common_mode": "DC 0.9V",
        "v3_vplus_input": "DC 0.9V",
        "v5_vminus_input": "DC 0.9V",
        "spice": """
.op
.control
set nobreak
set nomoremode
run
let power_val = v(vdd)*(-i(V2))
let current_val = (-i(V2))
echo 'POWER:' $&power_val
echo 'CURRENT:' $&current_val
.endc
"""
    }
}

# Units mapping for documentation
UNITS_MAP = {
    'DC_GAIN': 'dB',
    'SLEW_RATE_POS': 'V/s', 
    'SLEW_RATE_NEG': 'V/s',
    'POWER': 'W',
    'CURRENT': 'A',
    'GBW': 'Hz'
}

if __name__ == "__main__":
    build_and_simulate_variants(
        variants=VARIANTS,
        tests=TESTS,
        circuit_type="OpAmp",
        template_dir="template",
        units_map=UNITS_MAP
    )
