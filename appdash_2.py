import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import datetime
import dash_bootstrap_components as dbc
from flask_caching import Cache

# Initialisation de l'application Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
# Initialisation du cache pour améliorer les performances
cache = Cache(app.server, config={'CACHE_TYPE': 'simple'})
# Données d'exemple
df = pd.DataFrame({
    "date": pd.date_range(start="2024-03-01", periods=10, freq="D"),
    "value": [10, 20, 15, 30, 25, 40, 35, 50, 45, 60]
})
# Mise en page de l'application
app.layout = html.Div(children=[
  html.H1("Prévisions de données", style={'text-align': 'center'}),
    dbc.Row([
      dbc.Col([
        html.Label("Date de début"),
        dcc.DatePickerSingle(
            id='start-date-picker',
            min_date_allowed=df['date'].min(),
            max_date_allowed=df['date'].max(),
            date=df['date'].min(),
        ),
      ], width=4),
      dbc.Col([
        html.Label("Date de fin"),
        dcc.DatePickerSingle(
            id='end-date-picker',
            min_date_allowed=df['date'].min(),
            max_date_allowed=df['date'].max(),
            date=df['date'].max(),
        ),
      ], width=4),
      dbc.Col([
        html.Button('Réinitialiser les dates', id='reset-btn', n_clicks=0),
      ], width=4),
    ], style={'padding': '20px'}),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='graph')
        ], width=8),

        dbc.Col([
            html.Div(id='stats', style={'padding': '10px', 'font-size': '18px'}),
        ], width=4),
    ], style={'padding': '20px'}),
])
# Callback pour mettre à jour le graphique en fonction des dates sélectionnées
@app.callback(
    [Output('graph', 'figure'),
     Output('stats', 'children')],
    [Input('start-date-picker', 'date'),
     Input('end-date-picker', 'date')]
)
@cache.memoize(timeout=60)  # Mise en cache pour améliorer la performance
def update_graph_and_stats(start_date, end_date):
    # Convertir les dates en format datetime
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

    # Filtrer les données selon les dates sélectionnées
    filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    # Créer la figure avec Plotly
    fig = px.line(filtered_df, x="date", y="value", title="Évolution des valeurs")

    return fig, stats
# Callback pour réinitialiser les dates
@app.callback(
    [Output('start-date-picker', 'date'),
     Output('end-date-picker', 'date')],
    [Input('reset-btn', 'n_clicks')]
)
def reset_dates(n_clicks):
    if n_clicks > 0:
        return [df['date'].min().strftime("%Y-%m-%d"), df['date'].max().strftime("%Y-%m-%d")]
    return [df['date'].min().strftime("%Y-%m-%d"), df['date'].max().strftime("%Y-%m-%d")]
# Lancer l'application
if __name__ == '__main__':
    app.run_server(debug=True)
