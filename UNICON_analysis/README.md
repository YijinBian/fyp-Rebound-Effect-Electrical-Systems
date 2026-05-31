This is the python code for analyze UNICON dataset.
## File Description

- `config.py`: Defines dataset paths, model parameters, pricing settings, and system evaluation thresholds for the UNICON analysis.
- `data_load_unicon.py`: Loads, cleans, filters, and resamples the UNICON Building 14 electricity data.
- `data_load_test.py`: Tests whether the UNICON data loading and pre-processing process works correctly.
- `monte_carlo_simulation_unicon.py`: Implements the Monte Carlo rebound simulation for the UNICON building-level load profile.
- `monte_carlo_test.py`: Tests the Monte Carlo simulation output using baseline, efficiency-only, and rebound-affected scenarios.
- `main.py`: Runs the full UNICON supplementary robustness check, including rebound modelling, sensitivity analysis, pricing response, system evaluation, and result plotting.
