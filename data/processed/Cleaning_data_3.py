import pandas as pd
import numpy as np
import glob
import os
from datetime import datetime
import matplotlib.pyplot as plt

def load_rte_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines()]
        
        current_date = None
        data = []
        
        for i, line in enumerate(lines):
            if i < 5:
                print(f"Ligne {i}: {line}")
            
            if "Journée du" in line:
                current_date = line.split("du ")[1].strip()
                print(f"Trouvé date: {current_date}")
            
            elif current_date and ';' in line:
                parts = [part.strip() for part in line.split(';')]
                if len(parts) == 4: 
                    parts[1:] = [
                        float(p.replace(',', '.')) if p.replace(',', '').isdigit() else np.nan 
                        for p in parts[1:]
                    ]
                    data.append([current_date] + parts)
        
        if not data:
            print(f"Aucune donnée valide dans {file_path}")
            return pd.DataFrame()
        
        df = pd.DataFrame(data, columns=['Date', 'Heure', 'PrevisionJ-1', 'PrevisionJ', 'Consommation'])
        
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
    df = df.dropna(subset=['DateTime'])
    
    df = df.sort_values('DateTime').set_index('DateTime')
    
    df = df[~df.index.duplicated(keep='first')]
    
    df = df.resample('15T').asfreq()
    
    for col in ['PrevisionJ-1', 'PrevisionJ', 'Consommation']:
        if col in df.columns:
            df[col] = df[col].interpolate(method='time', limit_direction='both')
            
            if df[col].isna().any():
                df[col] = df.groupby(df.index.hour)[col].transform(
                    lambda x: x.fillna(x.median()))
    
    df['Hour'] = df.index.hour
    df['DayOfWeek'] = df.index.dayofweek
    df['IsWeekend'] = df['DayOfWeek'].isin([5,6]).astype(int)
    
    return df.reset_index()

def main():
    print("Traitement des données RTE...")
    
    files = glob.glob('conso_mix_RTE_*.csv')
    if not files:
        print("Aucun fichier trouvé. Fichiers disponibles:")
        print(os.listdir())
        return
    
    print(f"Fichiers trouvés: {files}")
    
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
    
    final_df = pd.concat(dfs)
    clean_df = clean_data(final_df)
    
    print("\n=== RÉSULTAT FINAL ===")
    print(f"Période: {clean_df['DateTime'].min()} à {clean_df['DateTime'].max()}")
    print(f"Nombre de points: {len(clean_df)}")
    print("\nValeurs manquantes résiduelles:")
    print(clean_df.isnull().sum())
    
    plt.figure(figsize=(15,5))
    clean_df.set_index('DateTime')['Consommation'].plot(title='Consommation électrique (MW)')
    plt.grid()
    plt.show()
    
    output_file = 'consommation_rte_clean.csv'
    clean_df.to_csv(output_file, index=False)
    print(f"\nDonnées sauvegardées dans {output_file}")

if __name__ == "__main__":
    main()
