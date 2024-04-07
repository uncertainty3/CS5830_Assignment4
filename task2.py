import os
import yaml
import pandas as pd

# Load global parameters from params.yaml file
global_param = yaml.safe_load(open('params.yaml'))['global']
month_cols = global_param['filter_cols']  # Filter columns specified in the global parameters
csv_files = global_param['download_dir']  # Directory containing downloaded CSV files

# Load prepare-specific parameters from params.yaml file
params = yaml.safe_load(open('params.yaml'))['prepare']

# Define the directory to store ground truth CSV files
gt_dir = os.path.join(*params['gt_dir'])  # Construct the path to the ground truth directory

# Create the directory for ground truth CSV files if it doesn't exist
os.makedirs(gt_dir, exist_ok=True)

# List CSV files in the download directory
csv = [file for file in os.listdir(csv_files) if file.endswith('.csv')]

# Iterate over each CSV file
for i, filename in enumerate(csv):
    download_path = os.path.join(csv_files, filename)  # Path to the downloaded CSV file
    df = pd.read_csv(download_path, low_memory=False)  # Read the CSV file into a DataFrame
    
    # Extract month from the DATE column and drop the DATE column
    df['Month'] = df['DATE'].apply(lambda x: int(x.split('-')[1]))  # Extract month from the DATE column
    df.drop('DATE', axis=1, inplace=True)  # Drop the DATE column
    
    # Extract the last row for each month and select only the specified month columns
    GT_df = df[['Month'] + month_cols].groupby('Month').tail(1).dropna(axis=1, thresh=1).reset_index(drop=True)
    
    # Save the ground truth DataFrame to a CSV file in the ground truth directory
    GT_df.to_csv(os.path.join(gt_dir, f'gtcsv_{i+1}.csv'), index=False)