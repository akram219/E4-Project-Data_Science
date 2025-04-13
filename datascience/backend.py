from flask import Flask, request, jsonify
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.ar_model import AutoReg
import json

app = Flask(__name__)

# Paramètres SARIMAX & AR
sarimax_model_params = None
ar_model_params = None

def load_sarimax_model():
    global sarimax_model_params
    try:
        print("Chargement des paramètres SARIMAX...")
        with open('sarimax_model_params.json', 'r') as f:
            sarimax_model_params = json.load(f)
        print("Paramètres SARIMAX chargés.")
    except Exception as e:
        print(f"Erreur lors du chargement des paramètres SARIMAX : {e}")

def load_ar_model():
    global ar_model_params
    try:
        print("Chargement des paramètres AR...")
        with open('ar_model_params.json', 'r') as f:
            ar_model_params = json.load(f)
        print("Paramètres AR chargés.")
    except Exception as e:
        print(f"Erreur lors du chargement des paramètres AR : {e}")

# Charger au démarrage
load_sarimax_model()
load_ar_model()

@app.route('/')
def index():
    return "Bienvenue sur l'API de Prédiction Électrique!"

@app.route('/predict/sarimax', methods=['POST'])
def predict_sarimax():
    global sarimax_model_params
    if not sarimax_model_params:
        return jsonify({"error": "Les paramètres du modèle SARIMAX ne sont pas chargés."}), 500
    if 'file' not in request.files:
        return jsonify({"error": "Aucun fichier n'a été envoyé."}), 400

    file = request.files['file']
    try:
        df = pd.read_csv(file, parse_dates=['DateTime'], index_col='DateTime')
        if 'Consommation' not in df.columns:
            return jsonify({"error": "La colonne 'Consommation' est manquante."}), 400

        model = sm.tsa.SARIMAX(
            df['Consommation'],
            order=sarimax_model_params['order'],
            seasonal_order=sarimax_model_params['seasonal_order']
        )
        fitted_model = model.fit(disp=False)
        prediction = fitted_model.predict(start=0, end=len(df)-1)

        stats = {
            "moyenne": round(df['Consommation'].mean(), 2),
            "min": round(df['Consommation'].min(), 2),
            "max": round(df['Consommation'].max(), 2),
            "mse": round(((df['Consommation'] - prediction) ** 2).mean(), 2)
        }

        derniere_valeur = round(df['Consommation'].iloc[-1], 2)
        prochaine_prediction = round(fitted_model.forecast(steps=1)[0], 2)

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

@app.route('/predict/ar', methods=['POST'])
def predict_ar():
    global ar_model_params
    if not ar_model_params:
        return jsonify({"error": "Les paramètres du modèle AR ne sont pas chargés."}), 500
    if 'file' not in request.files:
        return jsonify({"error": "Aucun fichier n'a été envoyé."}), 400

    file = request.files['file']
    try:
        df = pd.read_csv(file, parse_dates=['DateTime'], index_col='DateTime')
        df = df.dropna(subset=['Consommation'])

        if 'Consommation' not in df.columns:
            return jsonify({"error": "La colonne 'Consommation' est manquante."}), 400

        lag_order = ar_model_params['order'][0]
        model = AutoReg(df['Consommation'], lags=lag_order)
        fitted_model = model.fit()
        prediction = fitted_model.predict(start=lag_order, end=len(df)-1)

        cons_trimmed = df['Consommation'][lag_order:]

        stats = {
            "moyenne": round(cons_trimmed.mean(), 2),
            "min": round(cons_trimmed.min(), 2),
            "max": round(cons_trimmed.max(), 2),
            "mse": round(((cons_trimmed - prediction) ** 2).mean(), 2)
        }

        derniere_valeur = round(df['Consommation'].iloc[-1], 2)
        prochaine_prediction = round(fitted_model.forecast(steps=1)[0], 2)

        df_result = df.copy()
        df_result["Prediction"] = [None]*lag_order + prediction.tolist()
        data_sample = df_result.reset_index().head(10).to_dict(orient="records")

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
