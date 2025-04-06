import pandas as pd
import glob
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

# 1. Fonction de chargement des fichiers
def load_rte_file(file_path):
    """
    Charge un fichier RTE avec la structure :
    Ligne 1 : "Journée du DD/MM/YYYY"
    Ligne 2 : En-têtes (Heures|PrévisionJ-1|PrévisionJ|Consommation)
    """
    # Lire la date
    with open(file_path, 'r', encoding='utf-8') as f:
        date_line = f.readline()
        date_str = date_line.strip().split()[-1]  # Extrait "DD/MM/YYYY"
    
    # Charger les données
    df = pd.read_csv(file_path, skiprows=1, sep='|', encoding='utf-8')
    
    # Nettoyage des colonnes
    df.columns = [col.strip() for col in df.columns]
    
    # Création du timestamp complet
    df['date'] = pd.to_datetime(date_str + ' ' + df['Heures'], dayfirst=True)
    
    # Colonnes finales à conserver
    keep_cols = ['date', 'Consommation', 'PrévisionJ-1', 'PrévisionJ']
    return df[keep_cols]

# 2. Chargement de tous les fichiers
def load_all_files(pattern='conso_mix_RTE_*.csv'):
    files = glob.glob(pattern)
    if not files:
        raise ValueError(f"Aucun fichier trouvé avec le pattern {pattern}")
    
    data = pd.concat([load_rte_file(f) for f in files])
    return data.sort_values('date').reset_index(drop=True)

# 3. Nettoyage des données
def clean_data(df):
    """Nettoie le dataframe consolidé"""
    # Suppression des doublons temporels
    df = df.drop_duplicates('date', keep='first')
    
    # Gestion des valeurs manquantes
    df['Consommation'] = df['Consommation'].interpolate(method='time')
    
    # Détection des outliers (méthode IQR adaptée)
    Q1 = df['Consommation'].quantile(0.01)
    Q3 = df['Consommation'].quantile(0.99)
    IQR = Q3 - Q1
    mask = (df['Consommation'] >= (Q1 - 1.5 * IQR)) & (df['Consommation'] <= (Q3 + 1.5 * IQR))
    df = df[mask]
    
    return df

# 4. Feature Engineering
def add_features(df):
    """Ajoute les features temporelles"""
    # Features de base
    df['hour'] = df['date'].dt.hour
    df['day_of_week'] = df['date'].dt.dayofweek  # 0=lundi, 6=dimanche
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    # Features cycliques
    df['hour_sin'] = np.sin(2 * np.pi * df['hour']/24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour']/24)
    
    # Erreurs de prévision
    df['erreur_J-1'] = df['PrévisionJ-1'] - df['Consommation']
    df['erreur_J'] = df['PrévisionJ'] - df['Consommation']
    
    return df

# 5. Validation des données
def validate_data(df):
    """Valide la qualité des données"""
    print("\n=== Validation des données ===")
    print(f"Plage temporelle : {df['date'].min()} à {df['date'].max()}")
    print(f"Intervalle moyen : {pd.to_timedelta(np.diff(df['date']).mean())}")
    print(f"Valeurs manquantes :\n{df.isnull().sum()}")
    print(f"Doublons temporels : {df.duplicated('date').sum()}")
    
    # Vérification du pas temporel
    time_diff = np.diff(df['date'])
    freq_counts = pd.Series(time_diff).value_counts()
    print("\nFréquence des intervalles :")
    print(freq_counts.head())

# 6. Visualisation
def plot_sample_data(df, days=7):
    """Visualise un échantillon des données"""
    sample = df[df['date'] <= df['date'].min() + pd.Timedelta(days=days)]
    
    plt.figure(figsize=(15, 6))
    plt.plot(sample['date'], sample['Consommation'], label='Consommation réelle')
    plt.plot(sample['date'], sample['PrévisionJ'], label='Prévision J', linestyle='--')
    plt.title(f"Consommation électrique - {days} premiers jours")
    plt.ylabel("MW")
    plt.legend()
    plt.grid(True)
    plt.show()

# Pipeline complet
def main():
    # Chargement
    print("Chargement des fichiers...")
    df = load_all_files()
    
    # Nettoyage
    print("Nettoyage des données...")
    df_clean = clean_data(df)
    
    # Feature engineering
    print("Ajout des features...")
    df_final = add_features(df_clean)
    
    # Validation
    validate_data(df_final)
    
    # Visualisation
    plot_sample_data(df_final)
    
    # Sauvegarde
    df_final.to_csv('consommation_rte_clean.csv', index=False)
    print("\nDonnées sauvegardées dans 'consommation_rte_clean.csv'")

if __name__ == "__main__":
    main()