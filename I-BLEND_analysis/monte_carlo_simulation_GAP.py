import numpy as np
import pandas as pd
import config


def monte_carlo_simulation(base_profile_total, verbose=True):
    if verbose:
        print("simulation start")
        print(f"total number of students: {config.num_students}")

    avg_student_profile = base_profile_total / config.num_students

    #  1：build TOU price profile
    price_profile = pd.Series(config.tou_flat_price, index=avg_student_profile.index)

    #tou_peak_mask = (
            #(avg_student_profile.index.hour >= config.tou_peak_start) &
            #(avg_student_profile.index.hour <= config.tou_peak_end)
    #)

    #tou_offpeak_mask = (
            #(avg_student_profile.index.hour >= config.tou_offpeak_start) |
           # (avg_student_profile.index.hour <= config.tou_offpeak_end)
    #)

    #tou_flat_mask = ~(tou_peak_mask | tou_offpeak_mask)

    #price_profile.loc[tou_peak_mask] = config.tou_peak_price
    #price_profile.loc[tou_flat_mask] = config.tou_flat_price
    #price_profile.loc[tou_offpeak_mask] = config.tou_offpeak_price
    #normalized_load = avg_student_profile / avg_student_profile.max()
    #price_profile = config.base_price + config.price_sensitivity * normalized_load
    #base_weights = avg_student_profile / avg_student_profile.sum()

    if verbose:
        print(f"average peak for one student: {avg_student_profile.max():.2f} W")

    aggregated_rebound_load = np.zeros(len(base_profile_total))

    #price_profile = pd.Series(1.0, index=avg_student_profile.index)

    peak_mask = (avg_student_profile.index.hour >= 18) & (avg_student_profile.index.hour <= 22)
    #offpeak_mask = (avg_student_profile.index.hour >= 23) | (avg_student_profile.index.hour <= 7)
    #flat_mask = ~(peak_mask | offpeak_mask)

    #price_profile.loc[peak_mask] = 1.5
    #price_profile.loc[flat_mask] = 1.0
    #price_profile.loc[offpeak_mask] = 0.5
    #base_weights = avg_student_profile / avg_student_profile.sum()
    #price_effect = price_profile ** config.elasticity
    #dynamic_weights = base_weights * price_effect
    #dynamic_weights = dynamic_weights / dynamic_weights.sum()
    #tou_weights = base_weights * price_effect
    #tou_weights = tou_weights / tou_weights.sum()



    #  1：
    # 先找出 peak hour 区间

    peak_mask = (
        (base_profile_total.index.hour >= config.peak_start) &
        (base_profile_total.index.hour <= config.peak_end)
    )


    # 2：
    # 对 peak hours 内部再做加权
    # 原始负荷越高，rebound 越集中加在那里

    peak_profile = avg_student_profile[peak_mask].copy()

    if peak_profile.sum() > 0:
        peak_weights = peak_profile / peak_profile.sum()
    else:
        peak_weights = pd.Series(
            np.ones(len(peak_profile)) / len(peak_profile),
            index=peak_profile.index
        )

    base_weights = avg_student_profile / avg_student_profile.sum()

    if config.use_dynamic_pricing:
        normalized_load = avg_student_profile / avg_student_profile.max()
        price_profile = config.base_price + config.price_sensitivity * normalized_load
        price_effect = price_profile ** config.elasticity
        rebound_weights = base_weights * price_effect
        rebound_weights = rebound_weights / rebound_weights.sum()
    else:
        # without pricing: rebound is concentrated in peak hours
        rebound_weights = pd.Series(0.0, index=avg_student_profile.index)
        rebound_weights.loc[peak_mask] = peak_weights

    for i in range(config.num_students):
        # stochastic efficiency gap
        individual_gap_factor = np.random.normal(config.gap_mean, config.gap_std)
        individual_gap_factor = np.clip(individual_gap_factor, 0, 0.5)

        # stochastic rebound rate
        individual_rebound_rate = np.random.normal(config.rebound_mean, config.rebound_std)
        individual_rebound_rate = np.clip(individual_rebound_rate, 0, 1.0)

        # nominal technical saving
        nominal_savings = avg_student_profile * config.efficiency_rate

        # available saving after efficiency gap
        actual_available_savings = nominal_savings * (1 - individual_gap_factor)


        # 3：
        # 先计算总的 rebound energy
        # 不再直接逐小时按比例加回

        total_rebound_energy = actual_available_savings.sum() * individual_rebound_rate

        # 初始化逐小时 rebound 序列
        rebound_consumption = pd.Series(0.0, index=avg_student_profile.index)


        # 4：
        # 把总 rebound energy 按 peak hour 权重分配
        # 这样高负荷时段得到更多 rebound

        #rebound_consumption = total_rebound_energy * tou_weights
        #rebound_consumption = total_rebound_energy * dynamic_weights
        rebound_consumption = total_rebound_energy * rebound_weights

        # new student load
        student_new_load = avg_student_profile.copy()

        # efficiency reduces load across all hours
        student_new_load -= actual_available_savings

        # rebound mainly happens during weighted peak hours
        student_new_load += rebound_consumption

        # prevent negative load
        student_new_load = student_new_load.clip(lower=0)

        aggregated_rebound_load += student_new_load.values

        if verbose and i == 0:
            print(f"peak value for one student: {student_new_load.max():.2f} W")

    result_series = pd.Series(aggregated_rebound_load, index=base_profile_total.index)

    if verbose:
        print(f"peak value after aggregation: {result_series.max():.2f} W")

    # theoretical efficiency-only case (no gap, no rebound)
    ideal_efficiency_series = base_profile_total * (1 - config.efficiency_rate)


    return ideal_efficiency_series, result_series