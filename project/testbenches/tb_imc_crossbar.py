"""Testbench for IMC crossbar."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.imc_crossbar.imc_crossbar import generate
from library.testbenches.tb_imc import run

if __name__ == "__main__":
    run(generate, "imc_crossbar")
