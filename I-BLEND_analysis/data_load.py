import pandas as pd
import config

def load_data(file_path, value_column='power'):
    print('Loading data...')
    df = pd.read_csv(file_path)
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s', utc=True)
    df['datetime'] = df['datetime'].dt.tz_convert(config.timezone)
    df = df.set_index('datetime')
    df = df.sort_index()
    clean_series = pd.to_numeric(df[value_column], errors='coerce')
    clean_series = clean_series.dropna()
    resampled_data = clean_series.resample(config.resample_freq).mean().ffill()
    print('loading done')
    return resampled_data
