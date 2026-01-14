import numpy as np

# Parameters
freq = 66e6
vh = 1.8
vl = 0.0
period = 1/freq
samples_per_cycle = 64 
t_step = period / samples_per_cycle
tr = 50e-12 

def get_thermometer(val_3bit):
    return [1 if i < val_3bit else 0 for i in range(7)]

def generate_filesource():
    t_points = np.arange(0, period * 2.1, t_step)
    
    with open('dac_data.txt', 'w') as f:
        f.write("# Column 1: Time\n")
        f.write("# Columns 2-6: B0-B4 | 7-13: T0-T6 | 14-18: B0n-B4n | 19-25: T0n-T6n\n")
        
        for t in t_points:
            sine_val = int(127.5 * (np.sin(2 * np.pi * freq * t) + 1))
            msb_3 = (sine_val >> 5) & 0x07
            lsb_5 = sine_val & 0x1F
            therm = get_thermometer(msb_3)
            
            # 1. True Bits
            bits_b = [(lsb_5 >> i) & 1 for i in range(5)]
            bits_t = therm
            
            # 2. Complement Bits
            bits_bn = [1 - b for b in bits_b]
            bits_tn = [1 - t_bit for t_bit in bits_t]
            
            # Map logic to voltages
            all_signals = [vh if s else vl for s in (bits_b + bits_t + bits_bn + bits_tn)]
            
            # Write row: Time followed by all 24 values
            line = f"{t:.6e} " + " ".join(f"{val:.3f}" for val in all_signals)
            f.write(line + "\n")

if __name__ == "__main__":
    generate_filesource()