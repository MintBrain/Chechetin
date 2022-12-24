import os
import pandas as pd

def main(file_name, folder_name):
    new_path = fr'./{folder_name}'
    if not os.path.exists(new_path):
        os.makedirs(new_path)

    df = pd.read_csv(file_name)
    df['year'] = df['published_at'].apply(lambda x: x[0:4])
    df_group = df.groupby('year')

    for year, data in df_group:
        data.loc[:, data.columns != 'year'].to_csv(rf'{folder_name}\part_{year}.csv', index=False)

