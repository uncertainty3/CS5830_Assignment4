import os, yaml
import pandas as pd

global_param = yaml.safe_load(open('params.yaml'))['global']
param = yaml.safe_load(open('params.yaml'))['process']

csv_files = global_param['download_dir']
hour_cols = global_param['hourly_cols']
month_cols = global_param['filter_cols']

mon_to_hourly = {gt:hourly for gt,hourly in zip(month_cols,hour_cols)}
calc_dir = os.path.join(*param['calc_dir'])

os.makedirs(calc_dir, exist_ok=True)

csv = [file for file in os.listdir(csv_files) if file.endswith('.csv')]

for i,filename in enumerate(csv):
    download_path = os.path.join(csv_files, filename)
    df = pd.read_csv(download_path, low_memory=False)  # Read the downloaded CSV file into DataFrame

    df['Month'] = df['DATE'].apply( lambda x: int(x.split('-')[1]) )  
    df.drop('DATE',axis=1,inplace=True)

    # The below code filters out the columns which contain the monthly average data for ground truth
    GT_df = df[['Month']+month_cols].groupby('Month').tail(1).dropna(axis=1,thresh=1).reset_index(drop=True)

    valid_hourly = [mon_to_hourly[col] for col in list(GT_df.columns)[1:]]

    # Function to handle potential "s" suffix
    def convert_to_float(value):
        if type(value) == str:
            return float(value.rstrip('s'))  
        else: 
            return value

    # Apply the conversion function to pressure columns
    for col in valid_hourly:
        df[col] = df[col].apply(convert_to_float)

    calc_avgs = df[["Month"] + valid_hourly]

    # Get the calculated monthly averages
    calc_avgs_df = calc_avgs.groupby('Month')[valid_hourly].mean().reset_index()
    calc_avgs_df.to_csv( os.path.join(calc_dir, f'calc_csv_{i+1}.csv'),index=False)