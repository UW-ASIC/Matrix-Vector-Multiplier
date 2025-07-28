# Digital Project Configuration
PROJECT = DAC_Router
DESIGN_TOP := DAC_Router
RTL_FILES := $(shell find ../../../ -name "*.v" -o -name "*.sv")
RTL_FILES_H := $(shell find ../../ -name "*.vh" -o -name "*.svh")
TB_FILES := $(shell find ../../test -name "*_tb.v" -o -name "tb_*.v")
COCOTB_TEST_FILES := $(shell find ../../test -name "test_*.py")
TOPLEVEL_TB_MODULES := tb_DAC_Router
MODULE_TESTS := test_DAC_Router
PROJECT_TYPE = digital
