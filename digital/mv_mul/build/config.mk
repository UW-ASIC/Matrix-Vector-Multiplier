# Digital Project Configuration
PROJECT = mv_mul
DESIGN_TOP := mv_mul
RTL_FILES := $(shell find ../../../ -name "*.v" -o -name "*.sv")
RTL_FILES_H := $(shell find ../../ -name "*.vh" -o -name "*.svh")
TB_FILES := $(shell find ../../test -name "*_tb.v" -o -name "tb_*.v")
COCOTB_TEST_FILES := $(shell find ../../test -name "test_*.py")
TOPLEVEL_TB_MODULES := tb_mv_mul
MODULE_TESTS := test_mv_mul
PROJECT_TYPE = digital
