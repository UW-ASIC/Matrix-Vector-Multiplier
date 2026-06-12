"""Testbench for interleaved ADC."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.interleaved_adc.interleaved_adc import generate
from library.testbenches.tb_adc import run

if __name__ == "__main__":
    run(generate, "interleaved_adc")
