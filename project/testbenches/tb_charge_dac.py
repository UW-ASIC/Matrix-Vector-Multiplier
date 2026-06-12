"""Testbench for charge DAC."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.charge_dac.charge_dac import generate
from library.testbenches.tb_dac import run

if __name__ == "__main__":
    run(generate, "charge_dac")
