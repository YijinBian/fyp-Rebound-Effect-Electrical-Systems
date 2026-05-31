import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import config
import data_load_unicon
import monte_carlo_simulation_unicon


def evaluate_profile(load_profile, scenario_name):

    peak = load_profile.max()
    mean = load_profile.mean()
    par = peak / mean
    required_capacity = peak * (1 + config.capacity_margin)
    boundary_reached = (par > config.PAR_boundary) or (required_capacity > config.available_capacity)

    return {
        "Scenario": scenario_name,
        "Peak Load": peak,
        "Mean Load": mean,
        "PAR": par,
        "Required Capacity": required_capacity,
        "Boundary Reached": boundary_reached
    }


def print_evaluation_table(results):

    df = pd.DataFrame(results)

    print("\nSystem Impact Comparison:")
    print(df.to_string(index=False, formatters={
        "Peak Load": "{:.2f}".format,
        "Mean Load": "{:.2f}".format,
        "PAR": "{:.4f}".format,
        "Required Capacity": "{:.2f}".format
    }))

    return df


def plot_average_daily_profiles(baseline, efficiency_only, rebound_affected):

    hourly_baseline = baseline.groupby(baseline.index.hour).mean()
    hourly_efficiency = efficiency_only.groupby(efficiency_only.index.hour).mean()
    hourly_rebound = rebound_affected.groupby(rebound_affected.index.hour).mean()

    plt.figure(figsize=(10, 5))
    ##plt.plot(hourly_baseline.index, hourly_baseline.values, marker="o", label="Original Baseline")
    plt.plot(hourly_efficiency.index, hourly_efficiency.values, marker="o", linestyle="--", label="Efficiency-only")
    plt.plot(hourly_rebound.index, hourly_rebound.values, marker="o", label="Rebound-affected")

    plt.title(f"Average Daily Load Profiles - UNICON Building {config.unicon_building_id}")
    plt.xlabel("Hour of Day")
    plt.ylabel("Average Power (W)")
    plt.xticks(range(0, 24, 2))
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("unicon_average_daily_profiles.png", dpi=300, bbox_inches="tight")
    plt.show()


def plot_hourly_rebound_effect(efficiency_only, rebound_affected):

    rebound_diff = rebound_affected - efficiency_only
    hourly_diff = rebound_diff.groupby(rebound_diff.index.hour).mean()

    top_hours = hourly_diff.sort_values(ascending=False).head(5)

    print("\nTop 5 hours with strongest rebound effect:")
    print(top_hours)

    top_hours_df = pd.DataFrame({
        "Hour of Day": top_hours.index,
        "Average Rebound Difference": top_hours.values
    })

    print("\nTop Rebound Hours Table:")
    print(top_hours_df.to_string(index=False, formatters={
        "Average Rebound Difference": "{:.2f}".format
    }))

    plt.figure(figsize=(10, 5))
    plt.plot(hourly_diff.index, hourly_diff.values, marker="o")
    plt.axhline(0, color="black", linestyle="--", linewidth=1)

    plt.title(f"Average Hourly Rebound Effect - UNICON Building {config.unicon_building_id}")
    plt.xlabel("Hour of Day")
    plt.ylabel("Average Power Difference (W)")
    plt.xticks(range(0, 24, 2))
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("unicon_hourly_rebound_effect.png", dpi=300, bbox_inches="tight")
    plt.show()

    return top_hours_df


def rebound_level_sensitivity(baseline_load):

    original_rebound_mean = config.rebound_mean
    rebound_range = np.linspace(config.rebound_min, config.rebound_max, config.rebound_steps)

    results = []

    print("\nRebound Level Sensitivity Analysis:")

    for r in rebound_range:
        config.rebound_mean = r

        peak_runs = []
        par_runs = []
        capacity_runs = []

        for _ in range(config.simulation_runs):
            _, rebound_load = monte_carlo_simulation_unicon.monte_carlo_simulation_unicon(
                baseline_load,
                verbose=False
            )

            peak = rebound_load.max()
            mean = rebound_load.mean()
            par = peak / mean
            required_capacity = peak * (1 + config.capacity_margin)

            peak_runs.append(peak)
            par_runs.append(par)
            capacity_runs.append(required_capacity)

        avg_peak = np.mean(peak_runs)
        avg_par = np.mean(par_runs)
        avg_capacity = np.mean(capacity_runs)
        boundary_reached = (avg_par > config.PAR_boundary) or (avg_capacity > config.available_capacity)

        results.append({
            "Rebound Level": r,
            "Peak Load": avg_peak,
            "PAR": avg_par,
            "Required Capacity": avg_capacity,
            "Boundary Reached": boundary_reached
        })

        print(
            f"Rebound={r:.2f}, Peak={avg_peak:.2f}, PAR={avg_par:.4f}, "
            f"Required Capacity={avg_capacity:.2f}, Boundary Reached={boundary_reached}"
        )

    config.rebound_mean = original_rebound_mean

    df = pd.DataFrame(results)

    print("\nRebound Level Sensitivity Table:")
    print(df.to_string(index=False, formatters={
        "Rebound Level": "{:.2f}".format,
        "Peak Load": "{:.2f}".format,
        "PAR": "{:.4f}".format,
        "Required Capacity": "{:.2f}".format
    }))

    # Plot rebound level sensitivity
    plt.figure(figsize=(10, 5))
    plt.plot(df["Rebound Level"], df["Peak Load"], marker="o", label="Peak Load")
    plt.title("Peak Load Sensitivity to Rebound Level - UNICON")
    plt.xlabel("Rebound Level")
    plt.ylabel("Peak Load (W)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("unicon_rebound_level_peak_sensitivity.png", dpi=300, bbox_inches="tight")
    plt.show()

    plt.figure(figsize=(10, 5))
    plt.plot(df["Rebound Level"], df["Required Capacity"], marker="o", label="Required Capacity")
    plt.axhline(config.available_capacity, color="black", linestyle="--", linewidth=1, label="Available Capacity")
    plt.title("Required Capacity Sensitivity to Rebound Level - UNICON")
    plt.xlabel("Rebound Level")
    plt.ylabel("Required Capacity (W)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("unicon_rebound_level_capacity_sensitivity.png", dpi=300, bbox_inches="tight")
    plt.show()

    return df


def elasticity_sensitivity(baseline_load):

    original_elasticity = config.elasticity

    results = []

    print("\nElasticity Sensitivity Analysis:")

    for e in config.elasticity_levels:
        config.elasticity = e

        peak_runs = []
        par_runs = []
        capacity_runs = []

        for _ in range(config.simulation_runs):
            _, rebound_load = monte_carlo_simulation_unicon.monte_carlo_simulation_unicon(
                baseline_load,
                verbose=False
            )

            peak = rebound_load.max()
            mean = rebound_load.mean()
            par = peak / mean
            required_capacity = peak * (1 + config.capacity_margin)

            peak_runs.append(peak)
            par_runs.append(par)
            capacity_runs.append(required_capacity)

        avg_peak = np.mean(peak_runs)
        avg_par = np.mean(par_runs)
        avg_capacity = np.mean(capacity_runs)
        boundary_reached = (avg_par > config.PAR_boundary) or (avg_capacity > config.available_capacity)

        results.append({
            "Elasticity": e,
            "Peak Load": avg_peak,
            "PAR": avg_par,
            "Required Capacity": avg_capacity,
            "Boundary Reached": boundary_reached
        })

        print(
            f"Elasticity={e:.1f}, Peak={avg_peak:.2f}, PAR={avg_par:.4f}, "
            f"Required Capacity={avg_capacity:.2f}, Boundary Reached={boundary_reached}"
        )

    config.elasticity = original_elasticity

    df = pd.DataFrame(results)

    print("\nElasticity Sensitivity Table:")
    print(df.to_string(index=False, formatters={
        "Elasticity": "{:.1f}".format,
        "Peak Load": "{:.2f}".format,
        "PAR": "{:.4f}".format,
        "Required Capacity": "{:.2f}".format
    }))

    plt.figure(figsize=(10, 5))
    plt.plot(df["Elasticity"], df["Peak Load"], marker="o", label="Peak Load")
    plt.title("Peak Load Sensitivity to Price Elasticity - UNICON")
    plt.xlabel("Price Elasticity")
    plt.ylabel("Peak Load (W)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("unicon_elasticity_peak_sensitivity.png", dpi=300, bbox_inches="tight")
    plt.show()

    plt.figure(figsize=(10, 5))
    plt.plot(df["Elasticity"], df["PAR"], marker="o", label="PAR")
    plt.title("PAR Sensitivity to Price Elasticity - UNICON")
    plt.xlabel("Price Elasticity")
    plt.ylabel("PAR")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("unicon_elasticity_par_sensitivity.png", dpi=300, bbox_inches="tight")
    plt.show()

    return df


def pricing_comparison(baseline_load):

    original_pricing_setting = config.use_dynamic_pricing

    without_profiles = []
    with_profiles = []

    # Without pricing
    config.use_dynamic_pricing = False
    for _ in range(config.simulation_runs):
        _, load_without_pricing = monte_carlo_simulation_unicon.monte_carlo_simulation_unicon(
            baseline_load,
            verbose=False
        )
        without_profiles.append(load_without_pricing.groupby(load_without_pricing.index.hour).mean().values)

    # With pricing
    config.use_dynamic_pricing = True
    for _ in range(config.simulation_runs):
        _, load_with_pricing = monte_carlo_simulation_unicon.monte_carlo_simulation_unicon(
            baseline_load,
            verbose=False
        )
        with_profiles.append(load_with_pricing.groupby(load_with_pricing.index.hour).mean().values)

    config.use_dynamic_pricing = original_pricing_setting

    hour_index = np.arange(24)

    hourly_without_pricing = np.mean(np.array(without_profiles), axis=0)
    hourly_with_pricing = np.mean(np.array(with_profiles), axis=0)

    # Plot average daily profile comparison
    plt.figure(figsize=(10, 5))
    plt.plot(hour_index, hourly_without_pricing, marker="o", label="Without Pricing")
    plt.plot(hour_index, hourly_with_pricing, marker="o", label="With Dynamic Pricing")

    plt.title("Average Daily Power with Dynamic Pricing Effect - UNICON")
    plt.xlabel("Hour of Day")
    plt.ylabel("Average Power (W)")
    plt.xticks(range(0, 24, 2))
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("unicon_pricing_daily_comparison.png", dpi=300, bbox_inches="tight")
    plt.show()

    # Pricing difference
    pricing_diff = hourly_with_pricing - hourly_without_pricing

    plt.figure(figsize=(10, 5))
    plt.plot(hour_index, pricing_diff, marker="o")
    plt.axhline(0, color="black", linestyle="--", linewidth=1)

    plt.title("Power Difference under Dynamic Pricing - UNICON")
    plt.xlabel("Hour of Day")
    plt.ylabel("Average Power Difference (W)")
    plt.xticks(range(0, 24, 2))
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("unicon_pricing_difference.png", dpi=300, bbox_inches="tight")
    plt.show()

    return hourly_without_pricing, hourly_with_pricing, pricing_diff


def system_impact_summary_plot(baseline_load):

    original_pricing_setting = config.use_dynamic_pricing

    def run_average_metrics(use_pricing):
        config.use_dynamic_pricing = use_pricing

        peak_runs = []
        par_runs = []
        capacity_runs = []

        for _ in range(config.simulation_runs):
            _, rebound_load = monte_carlo_simulation_unicon.monte_carlo_simulation_unicon(
                baseline_load,
                verbose=False
            )

            peak = rebound_load.max()
            mean = rebound_load.mean()
            par = peak / mean
            capacity = peak * (1 + config.capacity_margin)

            peak_runs.append(peak)
            par_runs.append(par)
            capacity_runs.append(capacity)

        return np.mean(peak_runs), np.mean(par_runs), np.mean(capacity_runs)

    peak_without, par_without, cap_without = run_average_metrics(use_pricing=False)
    peak_with, par_with, cap_with = run_average_metrics(use_pricing=True)

    config.use_dynamic_pricing = original_pricing_setting

    labels = ["Peak Load", "PAR", "Required Capacity"]
    without_values = np.array([1.0, 1.0, 1.0])
    with_values = np.array([
        peak_with / peak_without,
        par_with / par_without,
        cap_with / cap_without
    ])

    x = np.arange(len(labels))
    width = 0.35

    plt.figure(figsize=(8, 5))
    plt.bar(x - width / 2, without_values, width, label="Without Pricing")
    plt.bar(x + width / 2, with_values, width, label="With Dynamic Pricing")

    plt.xticks(x, labels)
    plt.ylabel("Normalized Value")
    plt.title("System Impact of Dynamic Pricing - UNICON")
    plt.grid(True, axis="y", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("unicon_system_impact_dynamic_pricing.png", dpi=300, bbox_inches="tight")
    plt.show()

    print("\nSystem Impact of Dynamic Pricing:")
    print(f"Without Pricing: Peak={peak_without:.2f}, PAR={par_without:.4f}, Capacity={cap_without:.2f}")
    print(f"With Pricing:    Peak={peak_with:.2f}, PAR={par_with:.4f}, Capacity={cap_with:.2f}")
    print(f"Peak Ratio={peak_with / peak_without:.4f}")
    print(f"PAR Ratio={par_with / par_without:.4f}")
    print(f"Capacity Ratio={cap_with / cap_without:.4f}")


def main():
    print("Loading UNICON data...")
    baseline_load = data_load_unicon.load_unicon_data()

    print("\nRunning main Monte Carlo simulation...")
    efficiency_only, rebound_affected = monte_carlo_simulation_unicon.monte_carlo_simulation_unicon(
        baseline_load,
        verbose=True
    )

    # Main system impact comparison
    results = [
        evaluate_profile(baseline_load, "Original Baseline"),
        evaluate_profile(efficiency_only, "Efficiency-only"),
        evaluate_profile(rebound_affected, "Rebound-affected")
    ]

    system_df = print_evaluation_table(results)

    rebound_impact = (rebound_affected.max() - efficiency_only.max()) / efficiency_only.max() * 100
    peak_reduction = (rebound_affected.max() - baseline_load.max()) / baseline_load.max() * 100

    print(f"\nRebound impact relative to efficiency-only peak: {rebound_impact:.2f}%")
    print(f"Peak change from original baseline to rebound-affected: {peak_reduction:.2f}%")

    # Plots and analyses
    plot_average_daily_profiles(baseline_load, efficiency_only, rebound_affected)
    top_hours_df = plot_hourly_rebound_effect(efficiency_only, rebound_affected)

    rebound_df = rebound_level_sensitivity(baseline_load)
    elasticity_df = elasticity_sensitivity(baseline_load)

    pricing_comparison(baseline_load)
    system_impact_summary_plot(baseline_load)

    # Save result tables as CSV
    system_df.to_csv("unicon_system_impact_comparison.csv", index=False)
    top_hours_df.to_csv("unicon_top_rebound_hours.csv", index=False)
    rebound_df.to_csv("unicon_rebound_level_sensitivity.csv", index=False)
    elasticity_df.to_csv("unicon_elasticity_sensitivity.csv", index=False)

    print("\nAll UNICON analysis completed.")
    print("Figures and CSV result tables have been saved.")


if __name__ == "__main__":
    main()