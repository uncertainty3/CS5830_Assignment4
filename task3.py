import os, yaml
import pandas as pd

# Load global parameters from params.yaml file
global_param = yaml.safe_load(open('params.yaml'))['global']
# Load process-specific parameters from params.yaml file
param = yaml.safe_load(open('params.yaml'))['process']

# Extract parameters
csv_files = global_param['download_dir']  # Directory containing CSV files
hour_cols = global_param['hourly_cols']  # Hourly columns in the CSV files
month_cols = global_param['filter_cols']  # Monthly columns in the CSV files

# Mapping of monthly columns to corresponding hourly columns
mon_to_hourly = {gt: hourly for gt, hourly in zip(month_cols, hour_cols)}
calc_dir = os.path.join(*param['calc_dir'])  # Directory to store calculated CSV files

# Create the directory for calculated CSV files if it doesn't exist
os.makedirs(calc_dir, exist_ok=True)

# List CSV files in the download directory
csv = [file for file in os.listdir(csv_files) if file.endswith('.csv')]

# Iterate over each CSV file
for i, filename in enumerate(csv):
    download_path = os.path.join(csv_files, filename)
    df = pd.read_csv(download_path, low_memory=False)  # Read CSV file into DataFrame

    # Extract month from the DATE column and drop the DATE column
    df['Month'] = df['DATE'].apply(lambda x: int(x.split('-')[1]))
    df.drop('DATE', axis=1, inplace=True)

    # Extract monthly columns and remove NaN values
    GT_df = df[['Month'] + month_cols].groupby('Month').tail(1).dropna(axis=1, thresh=1).reset_index(drop=True)

    # Get valid hourly columns corresponding to the monthly columns
    valid_hourly = [mon_to_hourly[col] for col in list(GT_df.columns)[1:]]

    # Define function to convert string values to float
    def convert_to_float(value):
        if type(value) == str:
            return float(value.rstrip('s'))  # Remove 's' from the end of the string and convert to float
        else:
            return value

    # Apply conversion function to valid hourly columns
    for col in valid_hourly:
        df[col] = df[col].apply(convert_to_float)

    # Extract monthly averages for valid hourly columns
    calc_avgs = df[["Month"] + valid_hourly].groupby('Month')[valid_hourly].mean().reset_index()

    # Save calculated averages to CSV file in the calc_dir directory
    calc_avgs.to_csv(os.path.join(calc_dir, f'calc_csv_{i+1}.csv'), index=False)