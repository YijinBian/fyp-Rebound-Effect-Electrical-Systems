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

## Datasets Included

## Data Availability

The raw datasets are not included in this repository due to file size and redistribution considerations. Please download the datasets from their official sources and place the required CSV files in the corresponding analysis folders.

### I-BLEND Dataset

I-BLEND is used as the main hostel-level case study.

Official dataset collection:  
https://springernature.figshare.com/collections/I-BLEND_a_campus_scale_commercial_and_residential_buildings_electrical_energy_dataset/3893581

Energy dataset download page:  
https://springernature.figshare.com/articles/dataset/Energy_dataset_of_IIITD/6007637

Related paper:  
https://www.nature.com/articles/sdata201915

Required files:
- `boys_hostel_mains.csv`
- `girls_hostel_mains.csv`

Place these files in the `I-BLEND_analysis/` folder before running the code.

### UNICON Dataset

UNICON is used as a supplementary robustness check with building-level electricity data.

Kaggle dataset page:  
https://www.kaggle.com/datasets/cdaclab/unicon

GitHub dataset page:  
https://github.com/CDAC-lab/UNICON

Required file:
- `building_submeter_consumption.csv`

Place this file in the `UNICON_analysis/` folder before running the code.

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
