# Custom LVS setup for MVM project
# Sources the standard Sky130 setup, then adds project-specific overrides.

# Source the standard PDK setup
source $env(NETGEN_SETUP_PDK)

# Ignore MIM capacitors in layout (circuit 1) — schematic uses ideal C elements
# which are stripped for LVS. The physical MIM caps in layout have no schematic
# counterpart, so we tell netgen to ignore them.
ignore class "-circuit1 sky130_fd_pr__cap_mim_m3_1"
ignore class "-circuit1 sky130_fd_pr__cap_mim_m3_2"

# Ignore varactors extracted from parasitic gate-cap structures
ignore class "-circuit1 sky130_fd_pr__cap_var_lvt"
ignore class "-circuit1 sky130_fd_pr__cap_var_hvt"
ignore class "-circuit1 sky130_fd_pr__cap_var"
