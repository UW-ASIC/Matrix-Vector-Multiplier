"""Generate stimulus for GEMM tapeout testbench."""
import random

VDD = 1.8
VREF = 0.9
N_ROWS = 4
N_COLS = 4
N_BITS = 4
C_UNIT = 50e-15
C_INT = 500e-15
CLK_PERIOD = 20e-9  # 50 MHz


def _expected_adc_code(weights, x_vec, col):
    """Compute expected ADC code from charge-sharing physics.

    V_col = sum(V_xi * w_ij * C_UNIT) / (C_INT + sum(w_ij) * C_UNIT)
    ADC code = floor(V_col / VREF * 16)
    """
    w_total = sum(weights[i][col] for i in range(N_ROWS))
    total_cap = C_INT + w_total * C_UNIT
    if total_cap == 0:
        return 0
    charge = sum(
        (x_vec[i] / 15.0 * VREF) * weights[i][col] * C_UNIT
        for i in range(N_ROWS)
    )
    v_col = charge / total_cap
    code = int(v_col / VREF * 16)
    return min(15, max(0, code))


def generate_stimulus(seed=42):
    """Generate random weight matrix, input vectors, and expected outputs."""
    random.seed(seed)

    # Random 4x4 weight matrix (4-bit values 0-15)
    weights = [[random.randint(0, 15) for _ in range(N_COLS)] for _ in range(N_ROWS)]

    # 4 input vectors (one per MVM cycle), each 4 elements of 4-bit
    inputs = [[random.randint(0, 15) for _ in range(N_ROWS)] for _ in range(4)]

    # Expected outputs: charge-sharing physics model
    expected = []
    for x_vec in inputs:
        y = [_expected_adc_code(weights, x_vec, j) for j in range(N_COLS)]
        expected.append(y)

    return {
        "weights": weights,
        "inputs": inputs,
        "expected": expected,
        "vdd": VDD,
        "vref": VREF,
        "clk_period": CLK_PERIOD,
    }


def weights_to_pin_values(weights):
    """Convert weight matrix to per-bit DC voltage values."""
    pin_vals = {}
    for i in range(N_ROWS):
        for j in range(N_COLS):
            for b in range(N_BITS):
                val = VDD if (weights[i][j] >> b) & 1 else 0
                pin_vals[f"wb_{i}{j}{b}"] = val
    return pin_vals


def input_to_voltage(code):
    """Convert 4-bit input code to DAC-equivalent voltage."""
    return code / 15.0 * VREF


if __name__ == "__main__":
    stim = generate_stimulus()
    print(f"Weights: {stim['weights']}")
    print(f"Inputs: {stim['inputs']}")
    print(f"Expected: {stim['expected']}")
