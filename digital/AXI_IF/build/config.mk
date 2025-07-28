# Digital Project Configuration
PROJECT = i2c_module
DESIGN_TOP := i2c_module
RTL_FILES := $(shell find ../../../ -name "*.v" -o -name "*.sv")
RTL_FILES_H := $(shell find ../../ -name "*.vh" -o -name "*.svh")
TB_FILES := $(shell find ../../test -name "*_tb.v" -o -name "tb_*.v")
COCOTB_TEST_FILES := $(shell find ../../test -name "test_*.py")
TOPLEVEL_TB_MODULES := tb_i2c_module
MODULE_TESTS := test_i2c_module
PROJECT_TYPE = digital
