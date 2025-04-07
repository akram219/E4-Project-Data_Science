import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from Cleaning_data import load_and_clean_data
import pickle

# Générer des données de série temporelle exemple (20 observations)
np.random.seed(42)
data = np.random.randn(20)  # Données aléatoires
df = pd.DataFrame(data, columns=["Consommation"])

# Créer un modèle SARIMAX
sarimax_model = SARIMAX(df['Consommation'], 
                        order=(1, 1, 1),    # Paramètres ARIMA (p,d,q)
                        seasonal_order=(1, 1, 1, 4),  # Paramètres saisonniers (P,D,Q,S)
                        enforce_stationarity=False,   # Permet d'ignorer les contraintes de stationnarité
                        enforce_invertibility=False)  # Permet d'ignorer les contraintes d'inversibilité

# Ajuster le modèle
sarimax_fitted = sarimax_model.fit()

# Sauvegarder le modèle SARIMAX dans un fichier pickle
with open('sarimax_model.pkl', 'wb') as file:
    pickle.dump(sarimax_fitted, file)

print("Modèle SARIMAX sauvegardé dans 'sarimax_model.pkl'")
