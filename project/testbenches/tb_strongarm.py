"""Testbench for strongarm comparator."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.strongarm.strongarm import generate
from library.testbenches.tb_comparator import run

if __name__ == "__main__":
    run(generate, "strongarm")
