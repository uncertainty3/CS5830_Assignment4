#Import necessary libraries
import os, yaml
import pandas as pd
from sklearn.metrics import r2_score

# Load parameters from params.yaml file
global_params = yaml.safe_load(open('params.yaml'))['global']
params = yaml.safe_load(open('params.yaml'))

# Construct directories and list CSV files
gt_dir = os.path.join(*params['prepare']['gt_dir'])  # Construct ground truth directory path
calc_dir = os.path.join(*params['process']['calc_dir'])  # Construct calculated data directory path
gt_csvs = [file for file in sorted(os.listdir(gt_dir)) if file.endswith('.csv')]  # List ground truth CSV files
calc_csvs = [file for file in sorted(os.listdir(calc_dir)) if file.endswith('.csv')]  # List calculated data CSV files

# Initialize DataFrame to store R2 scores
# The DataFrame will have columns corresponding to the variables in the ground truth CSV files
r2 = pd.DataFrame(columns=pd.read_csv(os.path.join(gt_dir, gt_csvs[0])).columns[1:])

# Iterate over pairs of ground truth and calculated CSV files
for gt, calc in zip(gt_csvs, calc_csvs):
    # Read ground truth and calculated data into DataFrames
    GT_df = pd.read_csv(os.path.join(gt_dir, gt))  # Read ground truth CSV into DataFrame
    calc_avgs_df = pd.read_csv(os.path.join(calc_dir, calc))  # Read calculated data CSV into DataFrame
    
    # Drop rows containing missing values (NaN) from ground truth DataFrame
    GT_df_no_na = GT_df.dropna()  # Remove rows with missing values from ground truth DataFrame
    calc_avgs_no_na = calc_avgs_df.iloc[GT_df_no_na.index]  # Match indices to remove corresponding rows from calculated data DataFrame
    
    # Compute R2 scores for each column
    r2_scores = []
    for col_num in range(1, len(GT_df_no_na.columns)):
        r2_scores.append(r2_score(GT_df_no_na.iloc[:, col_num], calc_avgs_no_na.iloc[:, col_num]))  # Calculate R2 score for each variable
    
    # Store R2 scores in DataFrame
    r2.loc[calc] = r2_scores  # Store R2 scores for calculated data CSV file in DataFrame

# Write R2 scores to CSV file
r2.to_csv('R2results.csv')  # Save DataFrame with R2 scores to CSV file