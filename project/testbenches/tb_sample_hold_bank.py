"""Testbench for sample & hold bank."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.sample_hold_bank.sample_hold_bank import generate
from library.testbenches.tb_sample_hold import run

if __name__ == "__main__":
    run(generate, "sample_hold_bank")
