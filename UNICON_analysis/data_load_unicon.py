import pandas as pd
import config


def load_unicon_data(
    file_path=config.file_unicon,
    building_id=config.unicon_building_id,
    value_column="power",
    timezone=config.unicon_timezone,
    resample_freq=config.unicon_resample_freq
):

    print("Loading UNICON data...")

    df = pd.read_csv(file_path)

    print("Raw data shape:", df.shape)
    print("Columns:", list(df.columns))

    # Remove missing building_id rows
    df = df[df["building_id"].notna()].copy()

    # Convert building_id to numeric
    df["building_id"] = pd.to_numeric(df["building_id"], errors="coerce")
    df = df.dropna(subset=["building_id"])

    # Filter selected building
    df = df[df["building_id"] == building_id].copy()

    if df.empty:
        raise ValueError(f"No data found for building_id = {building_id}")

    print(f"Selected building_id: {building_id}")
    print("Selected data shape:", df.shape)

    # Convert timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df = df.dropna(subset=["timestamp"])

    # Convert timezone
    df["timestamp"] = df["timestamp"].dt.tz_convert(timezone)

    # Sort and set index
    df = df.sort_values("timestamp")
    df = df.set_index("timestamp")

    # Convert selected power column
    df[value_column] = pd.to_numeric(df[value_column], errors="coerce")

    # Clean invalid values
    load_series = df[value_column].dropna()
    load_series = load_series[load_series >= 0]

    # Optional unit conversion
    if config.unicon_power_kw_to_w:
        load_series = load_series * 1000

    # Resample to hourly mean
    hourly_load = load_series.resample(resample_freq).mean()

    # Fill small missing gaps
    hourly_load = hourly_load.ffill().bfill()

    print("Hourly load generated.")
    print("Hourly records:", len(hourly_load))
    print("Start time:", hourly_load.index.min())
    print("End time:", hourly_load.index.max())
    print("Mean load:", hourly_load.mean())
    print("Peak load:", hourly_load.max())
    print("Missing values after resampling:", hourly_load.isna().sum())

    return hourly_load