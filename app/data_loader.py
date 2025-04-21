import pandas as pd

def load_data(file_path):
    df = pd.read_excel(file_path)
    df['Time'] = pd.to_datetime(df['DepartTime'], errors='coerce').dt.time
    return df
