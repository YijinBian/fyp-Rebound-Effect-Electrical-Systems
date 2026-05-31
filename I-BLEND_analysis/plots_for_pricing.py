import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import config
import data_load
import monte_carlo_simulation_GAP


class PricingAndSystemImpactPlotter:
    def __init__(self, file_path, dataset_name="Boy Hostel"):
        self.file_path = file_path
        self.dataset_name = dataset_name

    def load_data(self):
        return data_load.load_data(self.file_path, value_column="power")

    def get_dynamic_pricing_components(self, hostel_load):
        """
        This function reconstructs the dynamic pricing logic used in monte_carlo_simulation_GAP.py.
        It shows how normalized load creates a dynamic price signal, and how the price signal
        modifies rebound allocation weights.
        """
        avg_student_profile = hostel_load / config.num_students

        # baseline allocation weight
        base_weights = avg_student_profile / avg_student_profile.sum()

        # dynamic pricing signal
        normalized_load = avg_student_profile / avg_student_profile.max()
        price_profile = config.base_price + config.price_sensitivity * normalized_load

        # price elasticity effect
        price_effect = price_profile ** config.elasticity

        # final rebound allocation weights under dynamic pricing
        rebound_weights = base_weights * price_effect
        rebound_weights = rebound_weights / rebound_weights.sum()

        # convert to hourly average
        hourly_normalized_load = normalized_load.groupby(normalized_load.index.hour).mean()
        hourly_price_profile = price_profile.groupby(price_profile.index.hour).mean()
        hourly_rebound_weights = rebound_weights.groupby(rebound_weights.index.hour).mean()

        # normalize rebound weight for visual comparison
        hourly_rebound_weights_normalized = hourly_rebound_weights / hourly_rebound_weights.max()

        return hourly_normalized_load, hourly_price_profile, hourly_rebound_weights_normalized

    def plot_dynamic_pricing_working_principle(self, save_path=None):
        hostel_load = self.load_data()

        hourly_load, hourly_price, hourly_weight = self.get_dynamic_pricing_components(hostel_load)

        plt.figure(figsize=(10, 5))
        plt.plot(hourly_load.index, hourly_load.values, marker="o", label="Normalized Load Level")
        plt.plot(hourly_price.index, hourly_price.values, marker="o", label="Dynamic Price Signal")
        plt.plot(hourly_weight.index, hourly_weight.values, marker="o", label="Rebound Allocation Weight")

        plt.axvspan(config.peak_start, config.peak_end, alpha=0.15, label="Peak Period")
        plt.title(f"Dynamic Pricing Working Principle ({self.dataset_name})")
        plt.xlabel("Hour of Day")
        plt.ylabel("Relative Value")
        plt.xticks(range(0, 24, 2))
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")

        plt.show()

    def run_average_metrics(self, hostel_load, use_pricing):
        original_pricing_setting = config.use_dynamic_pricing
        config.use_dynamic_pricing = use_pricing

        peak_runs = []
        par_runs = []
        capacity_runs = []

        for _ in range(config.simulation_runs):
            _, load = monte_carlo_simulation_GAP.monte_carlo_simulation(
                hostel_load, verbose=False
            )

            peak = load.max()
            mean = load.mean()
            par = peak / mean
            capacity = peak * (1 + config.capacity_margin)

            peak_runs.append(peak)
            par_runs.append(par)
            capacity_runs.append(capacity)

        config.use_dynamic_pricing = original_pricing_setting

        return np.mean(peak_runs), np.mean(par_runs), np.mean(capacity_runs)

    def plot_system_impact_summary(self, save_path=None):
        hostel_load = self.load_data()

        peak_no, par_no, cap_no = self.run_average_metrics(hostel_load, use_pricing=False)
        peak_yes, par_yes, cap_yes = self.run_average_metrics(hostel_load, use_pricing=True)

        labels = ["Peak Load", "PAR", "Required Capacity"]

        # normalized values: without pricing = 1.0
        without_pricing = np.array([1.0, 1.0, 1.0])
        with_pricing = np.array([
            peak_yes / peak_no,
            par_yes / par_no,
            cap_yes / cap_no
        ])

        x = np.arange(len(labels))
        width = 0.35

        plt.figure(figsize=(8, 5))
        plt.bar(x - width / 2, without_pricing, width, label="Without Pricing")
        plt.bar(x + width / 2, with_pricing, width, label="With Dynamic Pricing")

        plt.xticks(x, labels)
        plt.ylabel("Normalized Value")
        plt.title(f"System Impact of Dynamic Pricing ({self.dataset_name})")
        plt.grid(True, axis="y", alpha=0.3)
        plt.legend()
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")

        plt.show()

        print("\nSystem Impact Summary:")
        print(f"Without Pricing: Peak={peak_no:.2f}, PAR={par_no:.4f}, Capacity={cap_no:.2f}")
        print(f"With Pricing:    Peak={peak_yes:.2f}, PAR={par_yes:.4f}, Capacity={cap_yes:.2f}")
        print(f"Peak ratio={peak_yes / peak_no:.4f}")
        print(f"PAR ratio={par_yes / par_no:.4f}")
        print(f"Capacity ratio={cap_yes / cap_no:.4f}")



if __name__ == "__main__":
    plotter = PricingAndSystemImpactPlotter(
        config.file_boy_hostel,
        dataset_name="Boy Hostel"
    )

    plotter.plot_dynamic_pricing_working_principle(
        "dynamic_pricing_working_principle.png"
    )

    plotter.plot_system_impact_summary(
        "system_impact_dynamic_pricing.png"
    )

