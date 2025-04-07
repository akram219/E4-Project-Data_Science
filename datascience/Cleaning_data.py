import pandas as pd
import glob

def load_and_clean_data():
    files = glob.glob('C:/Users/elise/Documents/datascience/conso_mix_RTE_*')
    print(f"🔍 Fichiers trouvés : {files}")
    
    all_data = []

    for file in files:
        try:
            df = pd.read_excel(file, engine='openpyxl', header=1)
            df.columns = df.columns.str.strip()

            df.rename(columns={
                'Journée du 01/01/2023': 'Heures',
                'Heures': 'Heures',
                'Valeur': 'Consommation',
                'Unnamed: 1': 'PrévisionJ-1',
                'Unnamed: 2': 'PrévisionJ',
                'Unnamed: 3': 'Consommation'
            }, inplace=True)

            df = df[['Heures', 'Consommation']]
            df.dropna(inplace=True)
            df['Heures'] = pd.to_datetime(df['Heures'], format='%H:%M', errors='coerce')
            df = df.dropna(subset=['Heures'])
            df = df.set_index('Heures')
            all_data.append(df)
        except Exception as e:
            print(f"Erreur dans le fichier {file} : {e}")

    if all_data:
        full_df = pd.concat(all_data)
        return full_df
    else:
        return pd.DataFrame()  # DataFrame vide si aucun fichier valide
