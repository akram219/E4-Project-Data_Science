import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
import pickle
import warnings
from datetime import datetime
import os
warnings.filterwarnings("ignore")

def prepare_data():
    """Charge et prépare les données depuis le CSV nettoyé"""
    # Lecture du fichier CSV
    df = pd.read_csv('consommation_rte_clean.csv')
    
    # Vérifier si la colonne 'Heure' contient des valeurs manquantes
    if df['Heure'].isnull().any():
        print("Attention : Il y a des valeurs manquantes dans la colonne 'Heure'.")
        df['Heure'].fillna('00:00', inplace=True)  # Remplir les valeurs manquantes par '00:00'
    
    # Conversion des heures (format HH:MM)
    try:
        df['Heure'] = pd.to_datetime(df['Heure'], format='%H:%M').dt.time
    except Exception as e:
        print(f"Erreur lors de la conversion des heures : {str(e)}")
        return None
    
    # Création d'un index temporel complet (date + heure)
    base_date = datetime.now().date()
    df['Datetime'] = df['Heure'].apply(lambda x: datetime.combine(base_date, x))
    df.set_index('Datetime', inplace=True)
    
    # Vérification des données manquantes dans la colonne 'Consommation'
    if df['Consommation'].isnull().any():
        df['Consommation'] = df['Consommation'].interpolate()
    
    return df['Consommation']

def train_sarimax(series):
    """Entraîne et retourne un modèle SARIMAX optimisé"""
    # Paramètres optimisés pour des données avec une fréquence horaire
    order = (1, 0, 0)               # Un modèle AR simple (Auto-Régressif)
    seasonal_order = (1, 0, 0, 24)   # 24 périodes = une saisonnalité quotidienne

    model = SARIMAX(series,
                   order=order,
                   seasonal_order=seasonal_order,
                   enforce_stationarity=False,
                   enforce_invertibility=False)
    
    return model.fit(disp=True)

def save_model(model, filename):
    """Sauvegarde le modèle entraîné"""
    with open(filename, 'wb') as f:
        pickle.dump(model, f)
    print(f"Modèle SARIMAX sauvegardé dans '{filename}'")

if __name__ == "__main__":
    try:
        # 1. Préparation des données
        print("Chargement des données depuis consommation_rte_clean.csv...")
        consommation = prepare_data()
        
        # Si le fichier est incorrect et retourne None, nous arrêtons l'exécution
        if consommation is None:
            raise ValueError("Erreur dans la préparation des données")
        
        # échantillon plus petit pour tester plus rapidement
        consommation_sample = consommation[:10000]  # Par exemple, prendre les 10 000 premières observations
        
        print(f"Nombre d'observations : {len(consommation_sample)}")
        print(f"Plage horaire : {consommation_sample.index[0].time()} à {consommation_sample.index[-1].time()}")
        
        # 2. Entraînement du modèle
        print("\nEntraînement du modèle SARIMAX...")
        start_time = datetime.now()
        fitted_model = train_sarimax(consommation_sample)
        print(f"Temps d'entraînement : {datetime.now() - start_time}")
        
        # 3. Sauvegarde du modèle
        save_model(fitted_model, 'sarimax_model_rte.pkl')
        
        # 4. Validation
        print("\nRésumé du modèle:")
        print(fitted_model.summary())
        
    except Exception as e:
        print(f"\nErreur : {str(e)}")
        print("\nVérifiez que votre fichier CSV contient bien :")
        print("- Une colonne 'Heures' au format HH:MM")
        print("- Une colonne 'Consommation' avec des valeurs numériques")
        print("\nAperçu du fichier CSV :")
        print(pd.read_csv('consommation_rte_clean.csv').head())
