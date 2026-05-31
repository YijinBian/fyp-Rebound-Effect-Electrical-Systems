import matplotlib.pyplot as plt
import config
import data_load
import monte_carlo_simulation_GAP
import numpy as np


class SupportFigurePlotter:
    def __init__(self, file_path, dataset_name="Boys Hostel"):
        self.file_path = file_path
        self.dataset_name = dataset_name

    def load_profiles(self):
        hostel_load = data_load.load_data(self.file_path, value_column='power')
        load_ideal, load_rebound = monte_carlo_simulation_GAP.monte_carlo_simulation(
            hostel_load, verbose=False
        )
        return hostel_load, load_ideal, load_rebound

    def plot_rebound_modelling_figure(self, save_path=None):
        hostel_load, load_ideal, load_rebound = self.load_profiles()

        hourly_base = hostel_load.groupby(hostel_load.index.hour).mean()
        hourly_ideal = load_ideal.groupby(load_ideal.index.hour).mean()
        hourly_rebound = load_rebound.groupby(load_rebound.index.hour).mean()

        plt.figure(figsize=(9, 5))
        plt.plot(hourly_base.index, hourly_base.values, label='Baseline', linewidth=2)
        plt.plot(hourly_ideal.index, hourly_ideal.values, label='Efficiency Only', linestyle='--', linewidth=2)
        plt.plot(hourly_rebound.index, hourly_rebound.values, label='With Rebound', linewidth=2)

        plt.title(f'Average Daily Load Profiles ({self.dataset_name})')
        plt.xlabel('Hour of Day')
        plt.ylabel('Average Power (W)')
        plt.xticks(range(0, 24, 2))
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()


class SummaryBarPlotter:
    def __init__(self, file_path, dataset_name="Boys Hostel"):
        self.file_path = file_path
        self.dataset_name = dataset_name

    def plot_pricing_summary_bar(self, save_path=None):
        hostel_load = data_load.load_data(self.file_path, value_column='power')
        original_pricing_setting = config.use_dynamic_pricing

        def run_average_metrics(use_pricing):
            config.use_dynamic_pricing = use_pricing
            peak_runs = []
            par_runs = []
            capacity_runs = []

            for _ in range(config.simulation_runs):
                _, load = monte_carlo_simulation_GAP.monte_carlo_simulation(hostel_load, verbose=False)
                peak = load.max()
                mean = load.mean()
                par = peak / mean
                capacity = peak * (1 + config.capacity_margin)

                peak_runs.append(peak)
                par_runs.append(par)
                capacity_runs.append(capacity)

            return np.mean(peak_runs), np.mean(par_runs), np.mean(capacity_runs)

        peak_no, par_no, cap_no = run_average_metrics(False)
        peak_yes, par_yes, cap_yes = run_average_metrics(True)

        config.use_dynamic_pricing = original_pricing_setting

        labels = ['Peak', 'PAR', 'Capacity']

        # normalize by without-pricing values
        without_pricing = [1.0, 1.0, 1.0]
        with_pricing = [
            peak_yes / peak_no,
            par_yes / par_no,
            cap_yes / cap_no
        ]

        x = np.arange(len(labels))
        width = 0.35

        plt.figure(figsize=(8, 5))
        plt.bar(x - width / 2, without_pricing, width, label='Without Pricing')
        plt.bar(x + width / 2, with_pricing, width, label='With Pricing')

        plt.xticks(x, labels)
        plt.ylabel('Relative Value')
        plt.title(f'Normalized Pricing Mitigation Summary ({self.dataset_name})')
        plt.legend()
        plt.grid(True, axis='y', alpha=0.3)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()



if __name__ == "__main__":
    plotter = SupportFigurePlotter(config.file_boy_hostel, dataset_name="Boy Hostel")
    plotter.plot_rebound_modelling_figure("methodology_rebound_modelling.png")
    plotter = SummaryBarPlotter(config.file_boy_hostel, dataset_name="Boys Hostel")
    plotter.plot_pricing_summary_bar("conclusion_pricing_summary.png")