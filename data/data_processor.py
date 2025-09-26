import glob

import pandas as pd

"""Load data from a CSV file."""
def load_data(file_path) -> pd.DataFrame:
    return pd.read_csv(file_path)


"""Extract specified columns from the DataFrame."""
def extract_columns(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    return df[columns]


"""Remove entries with missing or zero IMO numbers."""
def remove_non_imo_entries(df: pd.DataFrame) -> pd.DataFrame:
    return df[df['IMO'].notna() & (df['IMO'] != 0) & (df['IMO'] != '') & (df['IMO'] != 'Unknown')]


"""Reindex the DataFrame to have a continuous index."""
def reindex_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.reset_index(drop=True)
    df.index += 1  # Start index from 1 instead of 0
    return df


"""Save the DataFrame to a CSV file."""
def save_dataframe(df: pd.DataFrame, file_path) -> None:
    new_file_path = file_path.replace('.csv', '-extracted.csv')
    df.to_csv(new_file_path, index=False)


def run(path: str = 'raw_data/2024/*/*/*.csv') -> None:
    for file in glob.glob(path):
        print(file)
        df = load_data(file)
        included_columns = ['# Timestamp', 'Latitude', 'Longitude', 'IMO', 'Name', 'Ship type', 'Destination', 'ETA']
        df_extracted = extract_columns(df, included_columns)
        df_only_ships = reindex_dataframe(remove_non_imo_entries(df_extracted))
        save_dataframe(df_only_ships, file)
