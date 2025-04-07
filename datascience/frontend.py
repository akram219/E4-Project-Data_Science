import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import requests
import json
import dash_bootstrap_components as dbc
from flask_caching import Cache

# Initialisation de l'application Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
cache = Cache(app.server, config={'CACHE_TYPE': 'simple'})

# Mise en page de l'application
app.layout = html.Div(children=[
    html.H1("Prédiction de la Consommation d'Énergie", style={'text-align': 'center'}),
    
    # Sélecteur de fichier
    dbc.Row([
        dbc.Col([
            html.Label("Téléchargez votre fichier CSV ou Excel"),
            dcc.Upload(
                id='upload-data',
                children=html.Button('Télécharger un fichier'),
                multiple=True
            ),
        ], width=12),
    ], style={'padding': '20px'}),
    
    # Affichage du graphique
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='prediction-graph')
        ], width=12),
    ], style={'padding': '20px'}),
    
    # Affichage des statistiques
    dbc.Row([
        dbc.Col([
            html.Div(id='statistics')
        ], width=12),
    ], style={'padding': '20px'}),
])

# Fonction pour traiter le fichier et envoyer la demande à Flask
@app.callback(
    [Output('prediction-graph', 'figure'),
     Output('statistics', 'children')],
    [Input('upload-data', 'contents')]
)
def update_graph(contents):
    if contents is None:
        return {}, ""
    
    # Préparer le fichier
    content_type, content_string = contents[0].split(',')
    decoded = base64.b64decode(content_string)
    
    # Utiliser Requests pour envoyer la demande POST à l'API Flask
    url = "http://127.0.0.1:5000/predict/sarimax"
    files = {'file': decoded}
    response = requests.post(url, files=files)
    
    if response.status_code == 200:
        data = response.json()
        if data:
            # Extraire les résultats et afficher le graphique
            df = pd.DataFrame(data['data_sample'])
            fig = px.line(df, x='Heures', y='Consommation', title="Consommation réelle vs Prédiction")
            
            # Affichage des statistiques
            stats = data['statistiques']
            stats_str = f"Max: {stats['max']}, Min: {stats['min']}, Moyenne: {stats['moyenne']}, MSE: {stats['mse']}"
            
            return fig, stats_str
    else:
        return {}, f"Erreur: {response.text}"

if __name__ == '__main__':
    app.run(debug=True)
