# generate_sarimax_model.py
import pandas as pd
import statsmodels.api as sm
import json
from datetime import datetime

# Charger les données
print("Chargement des données depuis consommation_rte_clean.csv...")
df = pd.read_csv('consommation_rte_clean.csv', parse_dates=['DateTime'], index_col='DateTime')

# Vérification des données
print(f"Aperçu des données :\n{df.head()}")

# Entraînement du modèle SARIMAX
print("Entraînement du modèle SARIMAX...")
sarimax_model = sm.tsa.SARIMAX(df['Consommation'], order=(1, 0, 0), seasonal_order=(1, 0, 0, 24))
sarimax_model_fitted = sarimax_model.fit(disp=False)

# Récupérer les paramètres du modèle
model_params = {
    'order': sarimax_model_fitted.model.order,  # Correction ici
    'seasonal_order': sarimax_model_fitted.model.seasonal_order  # Correction ici
}

# Sauvegarder les paramètres du modèle dans un fichier JSON
with open('sarimax_model_params.json', 'w') as f:
    json.dump(model_params, f)

print("Paramètres du modèle sauvegardés dans 'sarimax_model_params.json'")

# Afficher un résumé du modèle
print(sarimax_model_fitted.summary())
