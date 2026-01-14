import numpy as np

# Parameters
freq = 66e4
vh = 1.8
vl = 0.0
period = 1/freq
samples_per_cycle = 64 
t_step = period / samples_per_cycle
tr = 50e-12 # 50ps Rise/Fall time

def get_thermometer(val_3bit):
    return [1 if i < val_3bit else 0 for i in range(7)]

def generate_filesource():
    # Generate 2.1 cycles
    t_points = np.arange(0, period * 2.1, t_step)
    
    with open('dac_data.txt', 'w') as f:
        f.write("# Column 1: Time\n")
        f.write("# Columns 2-25: B0-B4, T0-T6, B0n-B4n, T0n-T6n\n")
        
        for t in t_points:
            # Calculate Sine value (8-bit: 0-255)
            sine_val = int(127.5 * (np.sin(2 * np.pi * freq * t) + 1))
            msb_3 = (sine_val >> 5) & 0x07
            lsb_5 = sine_val & 0x1F
            therm = get_thermometer(msb_3)
            
            # Map Logic to Vectors
            bits_b = [(lsb_5 >> i) & 1 for i in range(5)]
            bits_t = therm
            bits_bn = [1 - b for b in bits_b]
            bits_tn = [1 - t_bit for t_bit in bits_t]
            
            # Convert to Voltages
            signals = [vh if s else vl for s in (bits_b + bits_t + bits_bn + bits_tn)]
            data_str = " ".join(f"{val:.3f}" for val in signals)
            
            # 1. Start of transition (Snap to new value over tr)
            f.write(f"{t:.6e} {data_str}\n")
            
            # 2. End of hold period (Just before the next sample starts)
            # This ensures the signal stays flat until the next t_step begins
            t_hold = t + t_step - tr
            if t_hold > t: # Safety check
                f.write(f"{t_hold:.6e} {data_str}\n")

if __name__ == "__main__":
    generate_filesource()
    print("dac_data.txt generated with 50ps rise/fall timing.")