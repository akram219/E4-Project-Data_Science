import pandas as pd
import numpy as np
from datetime import datetime
import glob
import matplotlib.pyplot as plt


def load_and_clean_rte_data(file_pattern):
    files = glob.glob(file_pattern)
    if not files:
        raise ValueError(f"Aucun fichier trouvé avec le pattern {file_pattern}")

    all_dfs = []
    
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        current_date = None
        data = []

        for line in lines:
            if "Journée du" in line:
                current_date = line.split('du ')[1].strip()
            elif ';' in line and current_date:
                parts = line.strip().split(';')
                if len(parts) == 4: 
                    data.append([current_date] + parts)

        if data:
            df = pd.DataFrame(data, columns=['Date', 'Heure', 'PrevisionJ-1', 'PrevisionJ', 'Consommation']
            ) 
            df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)            
            for col in ['PrevisionJ-1', 'PrevisionJ', 'Consommation']:
                df[col] = pd.to_numeric(df[col].str.replace(',', '.'), errors='coerce')
            
            all_dfs.append(df)
    return pd.concat(all_dfs).sort_values(['Date', 'Heure'])
def clean_data(df):
    df['DateTime'] = pd.to_datetime(df['Date'].dt.strftime('%Y-%m-%d') + ' ' + df['Heure']
    )
    df = df.set_index('DateTime').drop(['Date', 'Heure'], axis=1)
    
    df = df.resample('15T').asfreq() 
    
    for col in df.columns:
        df[col] = df[col].interpolate(
            method='time',
            limit_direction='both'
        )
        
        if df[col].isna().any():
            hour_median = df.groupby(df.index.hour)[col].transform('median')
            df[col] = df[col].fillna(hour_median)
    

    df['Hour'] = df.index.hour
    df['DayOfWeek'] = df.index.dayofweek
    df['IsWeekend'] = df['DayOfWeek'].isin([5, 6]).astype(int)

    return df.reset_index()

def plot_missing_data(df, title):
    plt.figure(figsize=(12, 4))
    plt.title(title)
    plt.imshow(df.isna().T, aspect='auto', cmap='viridis', interpolation='nearest')
    plt.yticks(range(len(df.columns)), df.columns)
    plt.show()

try:
    raw_df = load_and_clean_rte_data('conso_mix_RTE_*.csv')
    print("Données brutes chargées :")
    print(raw_df.head())

    plot_missing_data(raw_df, "Données manquantes avant nettoyage")
  
    clean_df = clean_data(raw_df)
    print("\nDonnées nettoyées :")
    print(clean_df.head())
    plot_missing_data(clean_df, "Données manquantes après nettoyage")
    clean_df.to_csv('consommation_rte_clean.csv', index=False)
    print("\nDonnées sauvegardées dans 'consommation_rte_clean.csv'")

except Exception as e:
    print(f"Erreur : {str(e)}")
