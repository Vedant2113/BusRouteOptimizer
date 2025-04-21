import pandas as pd

def load_and_prepare_data(file_path):
    df = pd.read_excel(file_path)
    df['Time'] = pd.to_datetime(df['DepartTime'], errors='coerce').dt.time
    df['StopDisplay'] = df['Stop Location'].fillna('Unknown Stop') + " (" + df['Town'].fillna('Unknown Town') + ")"
    df['StopKey'] = df['Stop Location'].fillna('') + "||" + df['Town'].fillna('')
    stop_display_map = dict(zip(df['StopDisplay'], df['StopKey']))
    reverse_stop_display_map = {v: k for k, v in stop_display_map.items()}
    all_displays = sorted(df['StopDisplay'].dropna().unique())
    return df, all_displays, stop_display_map, reverse_stop_display_map
