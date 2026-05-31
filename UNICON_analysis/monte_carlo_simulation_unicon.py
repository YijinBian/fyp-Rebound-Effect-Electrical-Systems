import numpy as np
import pandas as pd
import config


def monte_carlo_simulation_unicon(base_profile_total, verbose=True):


    if verbose:
        print("Monte Carlo simulation start")
        print(f"number of representative units: {config.num_representative_units}")


    avg_unit_profile = base_profile_total / config.num_representative_units

    if verbose:
        print(f"average peak for one representative unit: {avg_unit_profile.max():.4f}")


    ideal_efficiency_series = base_profile_total * (1 - config.efficiency_rate)


    base_weights = avg_unit_profile / avg_unit_profile.sum()
    if config.use_dynamic_pricing:
        # Dynamic pricing based on normalized load level
        normalized_load = avg_unit_profile / avg_unit_profile.max()
        price_profile = config.base_price + config.price_sensitivity * normalized_load

        # Negative elasticity: higher price reduces rebound allocation
        price_effect = price_profile ** config.elasticity

        rebound_weights = base_weights * price_effect
        rebound_weights = rebound_weights / rebound_weights.sum()

    else:
        peak_mask = (
            (avg_unit_profile.index.hour >= config.peak_start) &
            (avg_unit_profile.index.hour <= config.peak_end)
        )

        peak_profile = avg_unit_profile[peak_mask].copy()

        if peak_profile.sum() > 0:
            peak_weights = peak_profile / peak_profile.sum()
        else:
            peak_weights = pd.Series(
                np.ones(len(peak_profile)) / len(peak_profile),
                index=peak_profile.index
            )

        rebound_weights = pd.Series(0.0, index=avg_unit_profile.index)
        rebound_weights.loc[peak_mask] = peak_weights

    aggregated_rebound_load = np.zeros(len(base_profile_total))

    for i in range(config.num_representative_units):
        # stochastic efficiency gap
        individual_gap_factor = np.random.normal(config.gap_mean, config.gap_std)
        individual_gap_factor = np.clip(individual_gap_factor, 0, 0.5)

        # stochastic rebound rate
        individual_rebound_rate = np.random.normal(config.rebound_mean, config.rebound_std)
        individual_rebound_rate = np.clip(individual_rebound_rate, 0, 1.0)

        nominal_savings = avg_unit_profile * config.efficiency_rate

        actual_available_savings = nominal_savings * (1 - individual_gap_factor)

        total_rebound_energy = actual_available_savings.sum() * individual_rebound_rate

        rebound_consumption = total_rebound_energy * rebound_weights


        unit_new_load = avg_unit_profile.copy()
        unit_new_load -= actual_available_savings
        unit_new_load += rebound_consumption


        unit_new_load = unit_new_load.clip(lower=0)

        aggregated_rebound_load += unit_new_load.values

        if verbose and i == 0:
            print(f"peak value for one representative unit: {unit_new_load.max():.4f}")

    result_series = pd.Series(aggregated_rebound_load, index=base_profile_total.index)

    if verbose:
        print(f"peak value after aggregation: {result_series.max():.2f}")

    return ideal_efficiency_series, result_series