file_girl_hostel = 'girls_hostel_mains.csv'
file_boy_hostel = 'boys_hostel_mains.csv'
file_transformer = 'all_transformer_power.csv'

num_students = 1000
efficiency_rate = 0.20
rebound_mean = 0.15
rebound_std = 0.10
simulation_runs = 200
resample_freq = '1h'
timezone = 'Asia/Kolkata'

# rebound more likely during peak hours
peak_start = 18
peak_end = 23

#galvin R 2014
gap_mean = 0.05
gap_std = 0.02

PAR_boundary = 3.5
capacity_margin = 0.15
# assumed available system capacity for boundary analysis
# 19000 for girl; 60000 for boy
available_capacity = 19000

# boundary sweep range
rebound_min = 0.05
rebound_max = 0.50
rebound_steps = 10

#TOU Pricing
off_peak_price = 0.5
flat_price = 1.0
peak_price = 1.5

tou_peak_start = 18
tou_peak_end = 22

tou_offpeak_start = 23
tou_offpeak_end = 7

tou_peak_price = 1.5
tou_flat_price = 1.0
tou_offpeak_price = 0.5

# price elasticity
elasticity = -0.3
elasticity_levels = [-0.1, -0.3, -0.5]

# dynamic pricing settings
base_price = 1.0
price_sensitivity = 0.8
use_dynamic_pricing = True