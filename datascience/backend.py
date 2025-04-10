from flask import Flask, request, jsonify
import pandas as pd
import pickle
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

app = Flask(__name__)

# Charger le modèle SARIMAX
try:
    with open('sarimax_model_rte.pkl', 'rb') as f:
        sarimax_model = pickle.load(f)
except Exception as e:
    print(f"Erreur lors du chargement du modèle: {str(e)}")
    sarimax_model = None

@app.route('/predict/sarimax', methods=['POST'])
def predict_sarimax():
    if 'file' not in request.files:
        return jsonify({"error": "Aucun fichier fourni"}), 400

    files = request.files.getlist('file')
    results = {}

    for file in files:
        try:
            # Lecture du fichier
            try:
                df = pd.read_excel(file, engine='openpyxl', header=1)
            except:
                try:
                    df = pd.read_excel(file, engine='xlrd', header=1)
                except:
                    file.stream.seek(0)
                    df = pd.read_csv(file.stream)

            # Nettoyage des noms de colonnes
            df.columns = df.columns.str.strip()
            df.rename(columns={
                'Journée du 01/01/2023': 'Heure',
                'Heure': 'Heure',
                'Valeur': 'Consommation',
                'Unnamed: 3': 'Consommation',
                'Consommation': 'Consommation',
            }, inplace=True)

            if 'Consommation' not in df.columns or 'Heure' not in df.columns:
                return jsonify({
                    "error": "Colonnes requises manquantes",
                    "colonnes_disponibles": list(df.columns),
                    "solution": "Assurez-vous que le fichier contient bien les colonnes 'Heure' et 'Consommation'"
                }), 400

            # Nettoyage de la colonne Heures
            df['Heure'] = pd.to_datetime(df['Heure'], errors='coerce')
            heures_invalides = df['Heure'].isna().sum()
            df.dropna(subset=['Heure'], inplace=True)

            # Conversion de Consommation en numérique
            df['Consommation'] = pd.to_numeric(df['Consommation'], errors='coerce')
            conso_invalides = df['Consommation'].isna().sum()
            df.dropna(subset=['Consommation'], inplace=True)

            if len(df) == 0:
                return jsonify({
                    "error": f"Le fichier {file.filename} est vide après nettoyage.",
                    "details": "Toutes les lignes ont été supprimées à cause de formats invalides."
                }), 400

            # Ajouter une date fixe aux heures
            df['Heure'] = df['Heure'].apply(lambda x: datetime.combine(datetime(2023, 1, 1), x.time()))
            df.set_index('Heure', inplace=True)
            df.sort_index(inplace=True)

            if sarimax_model is None:
                return jsonify({"error": "Modèle SARIMAX non chargé"}), 500

            # Prédiction
            forecast = sarimax_model.get_forecast(steps=len(df))
            df['Prediction'] = forecast.predicted_mean.values

            # Résultat
            results[file.filename] = {
                "metadata": {
                    "nb_observations": len(df),
                    "periode": f"{df.index[0]} à {df.index[-1]}"
                },
                "derniere_valeur": float(df['Consommation'].iloc[-1]),
                "prochaine_prediction": float(df['Prediction'].iloc[-1]),
                "statistiques": {
                    "moyenne": float(df['Consommation'].mean()),
                    "max": float(df['Consommation'].max()),
                    "min": float(df['Consommation'].min()),
                    "mse": float(((df['Consommation'] - df['Prediction']) ** 2).mean())
                },
                "data_sample": df.head(5).reset_index().to_dict(orient='records'),
                "avertissements": {
                    "lignes_supprimees_heures_invalides": int(heures_invalides),
                    "lignes_supprimees_conso_invalides": int(conso_invalides)
                } if heures_invalides > 0 or conso_invalides > 0 else {}
            }

        except ValueError as e:
            return jsonify({
                "error": f"Erreur de valeur dans {file.filename}",
                "details": str(e),
                "solution": "Vérifiez que les heures sont bien au format HH:MM et les consommations sont numériques"
            }), 400

        except Exception as e:
            return jsonify({
                "error": f"Erreur de traitement de {file.filename}",
                "type": type(e).__name__,
                "details": str(e)
            }), 500

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
