import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import datetime
import requests
from io import StringIO
import base64

# Initialisation de l'application Dash
app = dash.Dash(__name__)

# Configuration de l'API
API_URL = "http://127.0.0.1:5000/predict/sarimax"

# Mise en page de l'application
app.layout = html.Div(children=[
    html.H1("Dashboard de Prédiction de Consommation Électrique", style={'textAlign': 'center'}),
    
    # Section Upload
    html.Div([
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Glissez-déposez ou ',
                html.A('sélectionnez un fichier Excel')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            multiple=False
        ),
        html.Div(id='output-data-upload'),
    ], style={'width': '40%', 'margin': 'auto'}),
    
    # Section Graphique
    html.Div([
        dcc.Graph(id='consumption-graph'),
        dash_table.DataTable(
            id='prediction-table',
            page_size=10
        )
    ], style={'padding': '20px'}),
    
    # Section Prédiction
    html.Div([
        html.Button('Lancer la Prédiction', id='predict-button', n_clicks=0),
        html.Div(id='prediction-results')
    ])
])

# Callback pour l'upload de fichier
@app.callback(
    Output('output-data-upload', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_output(content, filename):
    if content is not None:
        return html.Div([
            html.H5(f"Fichier chargé : {filename}"),
            html.Hr()
        ])

# Callback pour la prédiction et affichage
@app.callback(
    [Output('consumption-graph', 'figure'),
     Output('prediction-table', 'data'),
     Output('prediction-table', 'columns'),
     Output('prediction-results', 'children')],
    Input('predict-button', 'n_clicks'),
    State('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def run_prediction(n_clicks, content, filename):
    if n_clicks > 0 and content is not None:
        try:
            # Décodage du fichier uploadé
            content_type, content_string = content.split(',')
            decoded = base64.b64decode(content_string)
            
            # Envoi au backend
            files = {'file': (filename, decoded)}
            response = requests.post(API_URL, files=files)
            
            if response.status_code == 200:
                result = response.json()
                data = list(result.values())[0]
                
                # Préparation des données pour le graphique
                df = pd.DataFrame(data['donnees_completes'])
                df['Heures'] = pd.to_datetime(df['Heures'])
                
                # Création du graphique
                fig = px.line(df, x='Heures', y=['Consommation', 'Prediction'],
                             title='Prédiction de Consommation')
                fig.update_layout(
                    xaxis_title='Heure',
                    yaxis_title='Consommation (MW)',
                    legend_title='Légende'
                )
                
                # Préparation du tableau
                table_data = df.to_dict('records')
                columns = [{"name": i, "id": i} for i in df.columns]
                
                # Résumé des prédictions
                stats = data['statistiques']
                summary = html.Div([
                    html.H4("Résumé des Prédictions"),
                    html.P(f"Dernière valeur connue: {data['derniere_valeur_connue']} MW"),
                    html.P(f"Prochaine prédiction: {data['prochaine_prediction']} MW"),
                    html.P(f"Moyenne: {stats['moyenne_consommation']:.2f} MW"),
                    html.P(f"Erreur quadratique moyenne: {stats['mse']:.2f}")
                ])
                
                return fig, table_data, columns, summary
            
            else:
                error = response.json().get('error', 'Erreur inconnue')
                return px.line(), [], [], html.Div(f"Erreur: {error}", style={'color': 'red'})
                
        except Exception as e:
            return px.line(), [], [], html.Div(f"Erreur: {str(e)}", style={'color': 'red'})
    
    return px.line(), [], [], html.Div()

# Lancer l'application
if __name__ == '__main__':
    # Démarrer sur un port différent du backend Flask
    app.run_server(debug=True, port=8050) 