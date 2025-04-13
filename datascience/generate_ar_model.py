# generate_ar_model.py
import pandas as pd
from statsmodels.tsa.ar_model import AutoReg
import json

# Charger les données
print("Chargement des données depuis consommation_rte_clean.csv...")
df = pd.read_csv('consommation_rte_clean.csv', parse_dates=['DateTime'], index_col='DateTime')

# Vérification des données
print(f"Aperçu des données :\n{df.head()}")

# Supprimer les NaN si nécessaire
df = df.dropna(subset=['Consommation'])

# Entraînement du modèle AR (ordre 5 par exemple)
lag_order = 5
print(f"Entraînement du modèle AR (lag={lag_order})...")
ar_model = AutoReg(df['Consommation'], lags=lag_order)
ar_model_fitted = ar_model.fit()

# Récupérer et sauvegarder les paramètres
model_params = {
    'order': [lag_order]
}

with open('ar_model_params.json', 'w') as f:
    json.dump(model_params, f)

print("Paramètres du modèle AR sauvegardés dans 'ar_model_params.json'")
