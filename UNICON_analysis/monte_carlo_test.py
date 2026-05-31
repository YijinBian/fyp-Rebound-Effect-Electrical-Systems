import config
import data_load_unicon
import monte_carlo_simulation_unicon


def evaluate_profile(load, name):
    peak = load.max()
    mean = load.mean()
    par = peak / mean
    required_capacity = peak * (1 + config.capacity_margin)
    boundary_reached = (par > config.PAR_boundary) or (required_capacity > config.available_capacity)

    print(f"\n{name}")
    print(f"Peak Load: {peak:.2f}")
    print(f"Mean Load: {mean:.2f}")
    print(f"PAR: {par:.4f}")
    print(f"Required Capacity: {required_capacity:.2f}")
    print(f"Boundary Reached: {boundary_reached}")


def main():
    load = data_load_unicon.load_unicon_data()

    efficiency_only, rebound_affected = monte_carlo_simulation_unicon.monte_carlo_simulation_unicon(
        load,
        verbose=True
    )

    evaluate_profile(load, "Original Baseline")
    evaluate_profile(efficiency_only, "Efficiency-only")
    evaluate_profile(rebound_affected, "Rebound-affected")

    rebound_impact = (rebound_affected.max() - efficiency_only.max()) / efficiency_only.max() * 100
    print(f"\nRebound impact relative to efficiency-only peak: {rebound_impact:.2f}%")


if __name__ == "__main__":
    main()