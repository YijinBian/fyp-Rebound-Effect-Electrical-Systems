# FYP Rebound Effect in Electrical Systems

This repository contains the Python source code for the Final Year Project:

**A Robust Framework for Assessing and Mitigating the Rebound Effect in Electrical Systems at Group Level**

## Project Overview

This project investigates the rebound effect in group-level electrical load profiles. The framework evaluates how energy efficiency improvement, behavioural rebound, load aggregation, and pricing response influence power system operation.

The main workflow includes:

- data pre-processing
- baseline load construction
- efficiency-only scenario construction
- rebound effect modelling
- Monte Carlo aggregation
- dynamic pricing and price elasticity modelling
- system-level evaluation

## Datasets

This project uses two public electricity consumption datasets:

1. I-BLEND dataset  
   Used as the main case study for hostel-level group load analysis.

2. UNICON dataset  
   Used as a supplementary robustness check with building-level submeter electricity data.

The raw datasets are not included in this repository due to file size and dataset redistribution considerations. Please download the datasets from their official sources and place them in the project folder before running the scripts.

## Main Files

- `config.py`  
  Stores model parameters, dataset paths, rebound assumptions, pricing settings, and system evaluation thresholds.

- `data_load.py`  
  Loads and pre-processes the I-BLEND hostel electricity data.

- `data_load_unicon.py`  
  Loads and pre-processes the UNICON Building 14 electricity data.

- `monte_carlo_simulation_GAP.py`  
  Implements the Monte Carlo rebound simulation for the I-BLEND case.

- `monte_carlo_simulation_unicon.py`  
  Implements the Monte Carlo rebound simulation for the UNICON supplementary case.

- `main.py`  
  Runs the main I-BLEND analysis.

- `main_unicon.py`  
  Runs the UNICON supplementary robustness check.
