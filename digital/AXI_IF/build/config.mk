# Digital Project Configuration
PROJECT = tt_if
DESIGN_TOP := tt_if
CONFIG_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
RTL_FILES := $(shell find $(CONFIG_DIR)../src -name "*.v" -o -name "*.sv" 2>/dev/null)
RTL_FILES_H := $(shell find $(CONFIG_DIR).. -name "*.vh" -o -name "*.svh")
TB_FILES := $(shell find $(CONFIG_DIR)../test -name "*_tb.sv" -o -name "tb_*.sv")

#### USED TO GENERATE FUNCTIONAL XSCHEM MODEL WITH VERILATOR #######
# File Path
TB_TOP := $(CONFIG_DIR)../test/tb_tt_if.sv
# The module name inside the TB_TOP
TB_TOP_MODULE := tb_tt_if

COCOTB_TEST_FILES := $(shell find $(CONFIG_DIR)../test -name "test_*.py")
TOPLEVEL_TB_MODULES := tb_tt_if
MODULE_TESTS := test_tt_if
PROJECT_TYPE = digital
