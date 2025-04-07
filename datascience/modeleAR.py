import pandas as pd
from statsmodels.tsa.ar_model import AutoReg
import pickle

# Exemple de données
data = [1.2, 1.5, 1.7, 2.1, 2.3, 2.4, 2.5, 2.7, 3.0, 3.1]

# Convertir les données en DataFrame
df = pd.DataFrame(data, columns=["value"])

# Entraîner le modèle AR
model = AutoReg(df["value"], lags=1)
ar_model = model.fit()

# Sauvegarder le modèle AR
with open('ar_model.pkl', 'wb') as file:
    pickle.dump(ar_model, file)

print("Modèle AR sauvegardé.")
