import glob

import pandas as pd
from data_processor import extract_columns

"""Split the DataFrame into separate files based on unique IMO numbers."""
def split_into_imo_files(file_path) -> None:
    extracted_df = pd.read_csv(file_path)
    unique_imos = extracted_df['IMO'].unique() # Get unique IMO numbers (i.e. unique ship ids)

    for imo in unique_imos:
        """Extract data for a specific IMO and convert to a DataFrame."""
        df_imo: pd.DataFrame = pd.DataFrame(extracted_df[extracted_df['IMO'] == imo])

        """Extract ship information from the first row of the IMO-specific DataFrame."""
        name = df_imo.iloc[0]['Name']
        ship_type = df_imo.iloc[0]['Ship type']
        destination = df_imo.iloc[0]['Destination']
        eta = df_imo.iloc[0]['ETA']
        imo_file_path = file_path.replace('.csv', f'-{imo}.csv')

        """Extract only relevant columns for the IMO-specific DataFrame."""
        df_imo = extract_columns(df_imo, ['# Timestamp', 'Latitude', 'Longitude'])

        """Save ship information to a text file"""
        imo_file_info_path = imo_file_path.replace('.csv', '-info.txt')
        with open(imo_file_info_path, 'w+') as f:
            f.write(f"IMO: {imo}\nName: {name}\nShip type: {ship_type}\nDestination: {destination}\nETA: {eta}\n")

        """Save the IMO-specific DataFrame to a CSV file."""
        df_imo.to_csv(imo_file_path, index=False)


def run(path: str = 'raw_data/2024/*/*/*-extracted.csv') -> None:
    for file in glob.glob(path):
        print(file)
        split_into_imo_files(file)