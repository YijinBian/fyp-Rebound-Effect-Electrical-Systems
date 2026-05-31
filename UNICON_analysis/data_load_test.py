import matplotlib.pyplot as plt
import config
import data_load_unicon


def main():
    load = data_load_unicon.load_unicon_data()

    print("\nFirst 5 rows:")
    print(load.head())

    print("\nBasic statistics:")
    print(load.describe())

    # Plot full time series
    plt.figure(figsize=(12, 5))
    plt.plot(load.index, load.values)
    plt.title(f"UNICON Building {config.unicon_building_id} Hourly Load Profile")
    plt.xlabel("Time")
    plt.ylabel("Power")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

    # Plot average daily profile
    hourly_avg = load.groupby(load.index.hour).mean()

    plt.figure(figsize=(10, 5))
    plt.plot(hourly_avg.index, hourly_avg.values, marker="o")
    plt.title(f"Average Daily Load Profile - Building {config.unicon_building_id}")
    plt.xlabel("Hour of Day")
    plt.ylabel("Average Power")
    plt.xticks(range(0, 24, 2))
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()