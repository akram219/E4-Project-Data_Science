from flask import Flask, request, jsonify
import pandas as pd
import statsmodels.api as sm
import json

app = Flask(__name__)

# Paramètres du modèle SARIMAX
sarimax_model_params = None

# Charger les paramètres depuis un fichier JSON
def load_sarimax_model():
    global sarimax_model_params
    try:
        print("Chargement des paramètres SARIMAX...")
        with open('sarimax_model_params.json', 'r') as f:
            sarimax_model_params = json.load(f)
        print("Paramètres du modèle chargés.")
    except FileNotFoundError:
        print("Erreur : Le fichier de paramètres SARIMAX est introuvable.")
    except Exception as e:
        print(f"Erreur lors du chargement des paramètres SARIMAX : {e}")

# Charger au démarrage
load_sarimax_model()

@app.route('/')
def index():
    return "Bienvenue sur l'API SARIMAX!"

@app.route('/predict/sarimax', methods=['POST'])
def predict_sarimax():
    global sarimax_model_params

    if not sarimax_model_params:
        return jsonify({"error": "Les paramètres du modèle SARIMAX ne sont pas chargés."}), 500

    if 'file' not in request.files:
        return jsonify({"error": "Aucun fichier n'a été envoyé."}), 400

    file = request.files['file']

    try:
        # Lecture du fichier CSV avec index sur 'DateTime'
        df = pd.read_csv(file, parse_dates=['DateTime'], index_col='DateTime')

        if 'Consommation' not in df.columns:
            return jsonify({"error": "La colonne 'Consommation' est manquante."}), 400

        # Création du modèle
        model = sm.tsa.SARIMAX(
            df['Consommation'],
            order=sarimax_model_params['order'],
            seasonal_order=sarimax_model_params['seasonal_order']
        )

        # Entraînement
        fitted_model = model.fit(disp=False)

        # Prédictions
        prediction = fitted_model.predict(start=0, end=len(df)-1)

        # Statistiques
        stats = {
            "moyenne": round(df['Consommation'].mean(), 2),
            "min": round(df['Consommation'].min(), 2),
            "max": round(df['Consommation'].max(), 2),
            "mse": round(((df['Consommation'] - prediction) ** 2).mean(), 2)
        }

        derniere_valeur = round(df['Consommation'].iloc[-1], 2)
        prochaine_prediction = round(fitted_model.forecast(steps=1)[0], 2)

        # Exemple de données pour affichage (les 10 premières lignes)
        df_result = df.copy()
        df_result["Prediction"] = prediction
        data_sample = df_result.head(10).reset_index().to_dict(orient="records")

        metadata = {
            "nb_observations": len(df),
            "periode": f"{df.index.min()} à {df.index.max()}"
        }

        return jsonify({
            "prediction": {
                "metadata": metadata,
                "derniere_valeur": derniere_valeur,
                "prochaine_prediction": prochaine_prediction,
                "statistiques": stats,
                "data_sample": data_sample
            }
        })

    except Exception as e:
        return jsonify({"error": f"Erreur lors du traitement du fichier : {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
