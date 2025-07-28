include ../config.mk

# Tool definitions
XSCHEM = xschem
NGSPICE = ngspice

.PHONY: all schematic spice clean setup

setup:
	@echo "Setting up symbol files..."
	@echo "Ignore errors below this ================"
	@mkdir -p ../../schematics/testbenches spice/testbenches || true; \
	mv ../../schematics/*_tb.sch ../../schematics/testbenches/ 2>/dev/null || true; \
	mv spice/*_tb.spice spice/testbenches/ 2>/dev/null || true;
	@echo "Ignore errors above this ================"

schematic: setup
	@echo "Opening xschem..."
	$(XSCHEM)

spice: setup
	@echo "Running SPICE simulations..."
	@if [ -d ../../netlist ]; then \
		for file in ../../netlist/*.spice; do \
			if [ -f "$$file" ]; then \
				echo "Running simulation: $$file"; \
				$(NGSPICE) -b "$$file"; \
			fi; \
		done; \
		if ! ls ../../netlist/*.spice 1> /dev/null 2>&1; then \
			echo "No SPICE files found in netlist directory"; \
		fi; \
	else \
		echo "No spice directory found"; \
	fi

clean:
	@echo "Cleaning generated files..."
	@rm -rf ../../netlist/*.spice
	@echo "Clean complete"
