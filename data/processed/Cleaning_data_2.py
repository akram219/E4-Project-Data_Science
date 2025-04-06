import pandas as pd
import glob
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

def load_rte_file(file_path):

    with open(file_path, 'r', encoding='utf-8') as f:
        date_line = f.readline()
        date_str = date_line.strip().split()[-1] 
    
    df = pd.read_csv(file_path, skiprows=1, sep='|', encoding='utf-8')
    
    df.columns = [col.strip() for col in df.columns]
    
    df['date'] = pd.to_datetime(date_str + ' ' + df['Heures'], dayfirst=True)
    
    keep_cols = ['date', 'Consommation', 'PrévisionJ-1', 'PrévisionJ']
    return df[keep_cols]

def load_all_files(pattern='conso_mix_RTE_*.csv'):
    files = glob.glob(pattern)
    if not files:
        raise ValueError(f"Aucun fichier trouvé avec le pattern {pattern}")
    
    data = pd.concat([load_rte_file(f) for f in files])
    return data.sort_values('date').reset_index(drop=True)

def clean_data(df):
    df = df.drop_duplicates('date', keep='first')
    
    df['Consommation'] = df['Consommation'].interpolate(method='time')
    
    Q1 = df['Consommation'].quantile(0.01)
    Q3 = df['Consommation'].quantile(0.99)
    IQR = Q3 - Q1
    mask = (df['Consommation'] >= (Q1 - 1.5 * IQR)) & (df['Consommation'] <= (Q3 + 1.5 * IQR))
    df = df[mask]
    
    return df

def add_features(df):
    df['hour'] = df['date'].dt.hour
    df['day_of_week'] = df['date'].dt.dayofweek  
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    df['hour_sin'] = np.sin(2 * np.pi * df['hour']/24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour']/24)
    
    df['erreur_J-1'] = df['PrévisionJ-1'] - df['Consommation']
    df['erreur_J'] = df['PrévisionJ'] - df['Consommation']
    
    return df

def validate_data(df):
    print("\n=== Validation des données ===")
    print(f"Plage temporelle : {df['date'].min()} à {df['date'].max()}")
    print(f"Intervalle moyen : {pd.to_timedelta(np.diff(df['date']).mean())}")
    print(f"Valeurs manquantes :\n{df.isnull().sum()}")
    print(f"Doublons temporels : {df.duplicated('date').sum()}")
    
    time_diff = np.diff(df['date'])
    freq_counts = pd.Series(time_diff).value_counts()
    print("\nFréquence des intervalles :")
    print(freq_counts.head())

def plot_sample_data(df, days=7):
    sample = df[df['date'] <= df['date'].min() + pd.Timedelta(days=days)]
    
    plt.figure(figsize=(15, 6))
    plt.plot(sample['date'], sample['Consommation'], label='Consommation réelle')
    plt.plot(sample['date'], sample['PrévisionJ'], label='Prévision J', linestyle='--')
    plt.title(f"Consommation électrique - {days} premiers jours")
    plt.ylabel("MW")
    plt.legend()
    plt.grid(True)
    plt.show()

def main():
    print("Chargement des fichiers...")
    df = load_all_files()
    
    print("Nettoyage des données...")
    df_clean = clean_data(df)
    
    print("Ajout des features...")
    df_final = add_features(df_clean)
    
    # 
    validate_data(df_final)
    
    plot_sample_data(df_final)
    
    df_final.to_csv('consommation_rte_clean.csv', index=False)
    print("\nDonnées sauvegardées dans 'consommation_rte_clean.csv'")

if __name__ == "__main__":
    main()
