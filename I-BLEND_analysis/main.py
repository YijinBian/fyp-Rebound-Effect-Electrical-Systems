import matplotlib.pyplot as plt
import config
import data_load
import monte_carlo_simulation_GAP
import numpy as np

def main():

    hostel_load = data_load.load_data(config.file_girl_hostel, value_column='power')
    if hostel_load.empty:
        print("no data!")

        return

    #load_ideal, load_rebound = monte_carlo_simulation.monte_carlo_simulation(hostel_load)
    #gap version
    initial_load_ideal, initial_load_rebound = monte_carlo_simulation_GAP.monte_carlo_simulation(hostel_load, verbose=True)
    peak_base = hostel_load.max()
    peak_rebound = initial_load_rebound.max()

    print('peak value')
    print(f"base peak: {peak_base}")
    print(f"rebound peak: {peak_rebound}")
    print(f"peak value change in %: {((peak_rebound - peak_base) / peak_base) * 100:.2f}%")
    mean_base = hostel_load.mean()
    mean_rebound = initial_load_rebound.mean()
    par_base = peak_base / mean_base
    par_rebound = peak_rebound / mean_rebound
    print(f"base PAR: {par_base:.4f}")
    print(f"rebound PAR: {par_rebound:.4f}")

    if par_rebound > par_base:
        print('Rebound exacerbates the peak-valley difference')

    elif par_rebound < par_base:
        print('Rebound smooths the load profile')

    else:
        print('Rebound does not change load volatility')

    var_base = hostel_load.var()
    var_rebound = initial_load_rebound.var()

    print(f"base variance: {var_base:.2f}")
    print(f"rebound variance: {var_rebound:.2f}")


    required_capacity_base = peak_base * (1 + config.capacity_margin)
    required_capacity_rebound = peak_rebound * (1 + config.capacity_margin)

    print(f"required capacity (base): {required_capacity_base:.2f} W")
    print(f"required capacity (rebound): {required_capacity_rebound:.2f} W")

    peak_ideal = initial_load_ideal.max()
    peak_rebound = initial_load_rebound.max()

    print(f"efficiency-only peak: {peak_ideal}")
    print(f"with rebound peak: {peak_rebound}")
    print(f"rebound impact relative to efficiency-only: {((peak_rebound - peak_ideal) / peak_ideal) * 100:.2f}%")

    par_results = []
    peak_results = []
    capacity_results = []
    boundary_flags = []

    original_rebound_mean = config.rebound_mean
    rebound_range = np.linspace(config.rebound_min, config.rebound_max, config.rebound_steps)

    for r in rebound_range:
        config.rebound_mean = r

        par_runs = []
        peak_runs = []
        capacity_runs = []



        for _ in range(config.simulation_runs):
            _, sweep_load_rebound = monte_carlo_simulation_GAP.monte_carlo_simulation(hostel_load, verbose=False)

            peak = sweep_load_rebound.max()
            mean = sweep_load_rebound.mean()
            par = peak / mean
            required_capacity = peak * (1 + config.capacity_margin)

            peak_runs.append(peak)
            par_runs.append(par)
            capacity_runs.append(required_capacity)

        avg_peak = np.mean(peak_runs)
        avg_par = np.mean(par_runs)
        avg_capacity = np.mean(capacity_runs)

        peak_results.append(avg_peak)
        par_results.append(avg_par)
        capacity_results.append(avg_capacity)

        reached = (avg_par > config.PAR_boundary) or (avg_capacity > config.available_capacity)
        boundary_flags.append(reached)

        print(
            f"Rebound={r:.2f}, Peak={avg_peak:.2f}, PAR={avg_par:.4f}, Required Capacity={avg_capacity:.2f}, Boundary Reached={reached}")
    config.rebound_mean = original_rebound_mean
    print("rebound levels:", rebound_range)
    print("PAR results:", par_results)

    boundary_found = False

    for r, par, cap, flag in zip(rebound_range, par_results, capacity_results, boundary_flags):
        if flag:
            print(f"\nBoundary first reached at rebound level = {r:.2f}")
            print(f"PAR = {par:.4f}")
            print(f"Required Capacity = {cap:.2f} W")
            boundary_found = True
            break

    if not boundary_found:
        print("\nBoundary not reached within the tested rebound range.")


    # elasticity sensitivity analysis
    elasticity_peak_results = []
    elasticity_par_results = []
    elasticity_capacity_results = []
    elasticity_boundary_results = []

    original_elasticity = config.elasticity

    print("\nElasticity sensitivity analysis:")

    for e in config.elasticity_levels:
        config.elasticity = e

        peak_runs = []
        par_runs = []
        capacity_runs = []

        for _ in range(config.simulation_runs):
            _, sensitivity_load_rebound = monte_carlo_simulation_GAP.monte_carlo_simulation(
                hostel_load, verbose=False
            )

            peak = sensitivity_load_rebound.max()
            mean = sensitivity_load_rebound.mean()
            par = peak / mean
            required_capacity = peak * (1 + config.capacity_margin)

            peak_runs.append(peak)
            par_runs.append(par)
            capacity_runs.append(required_capacity)

        avg_peak = np.mean(peak_runs)
        avg_par = np.mean(par_runs)
        avg_capacity = np.mean(capacity_runs)
        reached = (avg_par > config.PAR_boundary) or (avg_capacity > config.available_capacity)

        elasticity_peak_results.append(avg_peak)
        elasticity_par_results.append(avg_par)
        elasticity_capacity_results.append(avg_capacity)
        elasticity_boundary_results.append(reached)

        print(
            f"Elasticity={e:.1f}, Peak={avg_peak:.2f}, PAR={avg_par:.4f}, "
            f"Required Capacity={avg_capacity:.2f}, Boundary Reached={reached}"
        )

    # restore original elasticity
    config.elasticity = original_elasticity


    # hourly difference between rebound and baseline
    load_diff = initial_load_rebound - initial_load_ideal

    # average difference by hour of day
    hourly_diff = load_diff.groupby(load_diff.index.hour).mean()
    top_hours = hourly_diff.sort_values(ascending=False).head(5)

    print("\nTop 5 hours with strongest rebound effect:")
    print(top_hours)
    #rebound差值图看一下什么时候rebound比较强烈
    plt.figure(figsize=(10, 5))
    plt.plot(hourly_diff.index, hourly_diff.values, marker='o')
    plt.axhline(0, color='black', linestyle='--', linewidth=1)
    plt.title(f'Average Hourly Rebound Effect')
    plt.xlabel('Hour of Day')
    plt.ylabel('Average Power Difference (W)')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(12, 6))
    plt.plot(hostel_load.index, hostel_load, label='Baseline (Actual Data)', color='black', alpha=0.6)
    plt.plot(initial_load_ideal.index, initial_load_ideal, label='Efficiency Only (No Rebound)', color='green', linestyle='--')
    plt.plot(initial_load_rebound.index, initial_load_rebound, label='With Aggregated Rebound', color='blue')


    # average daily power profiles
    hourly_ideal = initial_load_ideal.groupby(initial_load_ideal.index.hour).mean()
    hourly_rebound = initial_load_rebound.groupby(initial_load_rebound.index.hour).mean()

    y_min = min(hourly_ideal.min(), hourly_rebound.min())
    y_max = max(hourly_ideal.max(), hourly_rebound.max())

    # without rebound effect
    plt.figure(figsize=(10, 5))
    plt.plot(hourly_ideal.index, hourly_ideal.values, marker='o')
    plt.ylim(y_min, y_max)
    plt.title('Average daily power without rebound effect')
    plt.xlabel('Hour of Day')
    plt.ylabel('Average Power (W)')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

    # with rebound effect
    plt.figure(figsize=(10, 5))
    plt.plot(hourly_rebound.index, hourly_rebound.values, marker='o')
    plt.ylim(y_min, y_max)
    plt.title('Average daily power profile with rebound effect')
    plt.xlabel('Hour of Day')
    plt.ylabel('Average Power (W)')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(12, 6))
    plt.plot(hostel_load.index, hostel_load, label='Baseline (Actual Data)', color='black', alpha=0.6)
    plt.plot(initial_load_ideal.index, initial_load_ideal, label='Efficiency Only (No Rebound)', color='green',
             linestyle='--')
    plt.plot(initial_load_rebound.index, initial_load_rebound, label='With Aggregated Rebound', color='blue')

    plt.title(f'Impact of Rebound Effect on Aggregated Load ({config.num_students} Students)')
    plt.xlabel('Time')
    plt.ylabel('Power (Watts)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(8, 5))
    plt.plot(config.elasticity_levels, elasticity_par_results, marker='o')
    plt.title('Elasticity Sensitivity of PAR')
    plt.xlabel('Price Elasticity')
    plt.ylabel('PAR')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


    # pricing effect comparison
    original_pricing_setting = config.use_dynamic_pricing

    without_profiles = []
    with_profiles = []

    # without pricing
    config.use_dynamic_pricing = False
    for _ in range(config.simulation_runs):
        _, load_without_pricing = monte_carlo_simulation_GAP.monte_carlo_simulation(hostel_load, verbose=False)
        without_profiles.append(load_without_pricing.groupby(load_without_pricing.index.hour).mean().values)

    # with pricing
    config.use_dynamic_pricing = True
    for _ in range(config.simulation_runs):
        _, load_with_pricing = monte_carlo_simulation_GAP.monte_carlo_simulation(hostel_load, verbose=False)
        with_profiles.append(load_with_pricing.groupby(load_with_pricing.index.hour).mean().values)

    # restore original setting
    config.use_dynamic_pricing = original_pricing_setting

    hour_index = np.arange(24)
    hourly_without_pricing = np.mean(np.array(without_profiles), axis=0)
    hourly_with_pricing = np.mean(np.array(with_profiles), axis=0)

    y_min = min(hourly_without_pricing.min(), hourly_with_pricing.min())
    y_max = max(hourly_without_pricing.max(), hourly_with_pricing.max())

    plt.figure(figsize=(10, 5))
    plt.plot(hour_index, hourly_without_pricing, marker='o', label='Without Pricing')
    plt.plot(hour_index, hourly_with_pricing, marker='o', label='With Pricing')
    plt.ylim(y_min, y_max)
    plt.title('Average Daily Power with Pricing Effect')
    plt.xlabel('Hour of Day')
    plt.ylabel('Average Power (W)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

    #difference under price effect
    pricing_diff = hourly_with_pricing - hourly_without_pricing
    plt.figure(figsize=(10, 5))
    plt.plot(hour_index, pricing_diff, marker='o')
    plt.axhline(0, color='black', linestyle='--', linewidth=1)
    plt.title('Power difference under pricing effect')
    plt.xlabel('Hour of Day')
    plt.ylabel('Average Power Difference (W)')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()
