import pandas as pd
import numpy as np
import glob
import os
from datetime import datetime
import matplotlib.pyplot as plt

def load_rte_file(file_path):
    """Charge un fichier RTE en gérant spécifiquement les lignes vides"""
    try:
        # Lecture du fichier en gardant les lignes vides pour le debug
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines()]
        
        current_date = None
        data = []
        
        for i, line in enumerate(lines):
            # Debug: afficher les premières lignes
            if i < 5:
                print(f"Ligne {i}: {line}")
            
            if "Journée du" in line:
                current_date = line.split("du ")[1].strip()
                print(f"Trouvé date: {current_date}")
            
            elif current_date and ';' in line:
                parts = [part.strip() for part in line.split(';')]
                if len(parts) == 4:  # Format attendu: Heure;PJ-1;PJ;Conso
                    # Conversion des nombres français
                    parts[1:] = [
                        float(p.replace(',', '.')) if p.replace(',', '').isdigit() else np.nan 
                        for p in parts[1:]
                    ]
                    data.append([current_date] + parts)
        
        if not data:
            print(f"Aucune donnée valide dans {file_path}")
            return pd.DataFrame()
        
        # Création du DataFrame
        df = pd.DataFrame(data, columns=['Date', 'Heure', 'PrevisionJ-1', 'PrevisionJ', 'Consommation'])
        
        # Conversion des types
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
        df['DateTime'] = pd.to_datetime(
            df['Date'].dt.strftime('%Y-%m-%d') + ' ' + df['Heure'],
            errors='coerce'
        )
        
        return df.dropna(subset=['DateTime'])
    
    except Exception as e:
        print(f"ERREUR avec {os.path.basename(file_path)}: {str(e)}")
        return pd.DataFrame()

def clean_data(df):
    """Nettoyage spécifique pour les données RTE avec lignes vides"""
    # 1. Suppression des lignes sans timestamp valide
    df = df.dropna(subset=['DateTime'])
    
    # 2. Tri chronologique
    df = df.sort_values('DateTime').set_index('DateTime')
    
    # 3. Suppression des doublons temporels
    df = df[~df.index.duplicated(keep='first')]
    
    # 4. Rééchantillonnage à 15 minutes
    df = df.resample('15T').asfreq()
    
    # 5. Imputation des valeurs manquantes
    for col in ['PrevisionJ-1', 'PrevisionJ', 'Consommation']:
        if col in df.columns:
            # Interpolation temporelle
            df[col] = df[col].interpolate(method='time', limit_direction='both')
            
            # Remplissage par médiane horaire
            if df[col].isna().any():
                df[col] = df.groupby(df.index.hour)[col].transform(
                    lambda x: x.fillna(x.median()))
    
    return df.reset_index()

def main():
    print("Traitement des données RTE...")
    
    # 1. Chargement
    files = glob.glob('conso_mix_RTE_*.csv')
    if not files:
        print("Aucun fichier trouvé. Fichiers disponibles:")
        print(os.listdir())
        return
    
    print(f"Fichiers trouvés: {files}")
    
    # 2. Chargement avec diagnostic
    dfs = []
    for f in files:
        print(f"\nTraitement de {os.path.basename(f)}...")
        df = load_rte_file(f)
        if not df.empty:
            dfs.append(df)
    
    if not dfs:
        print("\nAUCUNE DONNÉE VALIDE CHARGÉE. Causes possibles:")
        print("- Mauvais format de date/heure")
        print("- Séparateur différent (attendu: point-virgule)")
        print("- Lignes vides ou mal formatées")
        return
    
    # 3. Combinaison et nettoyage
    final_df = pd.concat(dfs)
    clean_df = clean_data(final_df)
    
    # 4. Vérification
    print("\n=== RÉSULTAT FINAL ===")
    print(f"Période: {clean_df['DateTime'].min()} à {clean_df['DateTime'].max()}")
    print(f"Nombre de points: {len(clean_df)}")
    print("\nValeurs manquantes résiduelles:")
    print(clean_df.isnull().sum())
    
    # 5. Visualisation
    plt.figure(figsize=(15,5))
    clean_df.set_index('DateTime')['Consommation'].plot(title='Consommation électrique (MW)')
    plt.grid()
    plt.show()
    
    # 6. Sauvegarde
    output_file = 'consommation_rte_clean.csv'
    clean_df.to_csv(output_file, index=False)
    print(f"\nDonnées sauvegardées dans {output_file}")

if __name__ == "__main__":
    main()