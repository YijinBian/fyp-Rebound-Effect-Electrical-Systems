# UNICON dataset settings
file_unicon = "building_submeter_consumption.csv"
unicon_building_id = 14
unicon_timezone = "Australia/Sydney"
unicon_resample_freq = "1h"

# Representative modelling units
# These are modelling units, not actual occupants.
num_representative_units = 1000

# Unit conversion
# Set to True only if the power column is confirmed to be in kW.
unicon_power_kw_to_w = True

# Rebound modelling settings
efficiency_rate = 0.20

rebound_mean = 0.15
rebound_std = 0.10

gap_mean = 0.05
gap_std = 0.02

simulation_runs = 200

# Peak period assumption
peak_start = 18
peak_end = 23

# System evaluation settings
capacity_margin = 0.15
PAR_boundary = 3.0
available_capacity = 35000

# Rebound sensitivity range
rebound_min = 0.05
rebound_max = 0.50
rebound_steps = 10

# Dynamic pricing settings
use_dynamic_pricing = True
base_price = 1.0
price_sensitivity = 0.8

# Price elasticity settings
elasticity = -0.3
elasticity_levels = [-0.1, -0.3, -0.5]