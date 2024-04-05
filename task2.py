import os
import yaml
import pandas as pd

global_param = yaml.safe_load(open('params.yaml'))['global']
month_cols = global_param['filter_cols']
csv_files = global_param['download_dir']

params = yaml.safe_load(open('params.yaml'))['prepare']

gt_dir = os.path.join(*params['gt_dir']) # 'data/gt'

os.makedirs(gt_dir, exist_ok = True)

csv = [file for file in os.listdir(csv_files) if file.endswith('.csv')]

for i,filename in enumerate(csv):
    download_path = os.path.join(csv_files, filename)
    df = pd.read_csv(download_path, low_memory=False)  # Read the downloaded CSV file into DataFrame
    
    df['Month'] = df['DATE'].apply( lambda x: int(x.split('-')[1]) )  
    df.drop('DATE',axis=1,inplace=True)

    # The below code filters out the columns which contain the monthly average data for ground truth
    GT_df = df[['Month']+month_cols].groupby('Month').tail(1).dropna(axis=1,thresh=1).reset_index(drop=True)
    GT_df.to_csv( os.path.join(gt_dir, f'gtcsv_{i+1}.csv') ,index=False)
