import os, yaml
import pandas as pd
import numpy as np
from sklearn.metrics import r2_score

global_params = yaml.safe_load(open('params.yaml'))['global']
params = yaml.safe_load(open('params.yaml'))

gt_dir = os.path.join(*params['prepare']['gt_dir'])
calc_dir = os.path.join(*params['process']['calc_dir'])
gt_csvs = [file for file in sorted(os.listdir(gt_dir)) if file.endswith('.csv')]
calc_csvs = [file for file in sorted(os.listdir(calc_dir)) if file.endswith('.csv')]

r2_df = pd.DataFrame(columns=pd.read_csv(os.path.join(gt_dir, gt_csvs[0])).columns[1:])
for gt,calc in zip(gt_csvs,calc_csvs):

    GT_df = pd.read_csv( os.path.join(gt_dir,gt))
    calc_avgs_df = pd.read_csv( os.path.join(calc_dir,calc))

    # Handle missing values (NA) in ground truth
    GT_df_wo_na = GT_df.dropna()  # Drop rows with NA in ground truth
    calc_avgs_wo_na = calc_avgs_df.iloc[GT_df_wo_na.index]  # Select corresponding rows in predictions

    # Calculate R2 score for each column
    r2_scores = []
    for col_num in range(1,len(GT_df_wo_na.columns)):
        r2_scores.append(r2_score(GT_df_wo_na.iloc[:,col_num], calc_avgs_wo_na.iloc[:,col_num]))

    r2_df.loc[calc] = r2_scores
r2_df.to_csv('R2results.csv')