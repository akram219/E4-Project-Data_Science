import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import datetime

# Initialisation de l'application Dash
app = dash.Dash(__name__)

# Données d'exemple
df = pd.DataFrame({
    "date": pd.date_range(start="2024-03-01", periods=10, freq="D"),
    "value": [10, 20, 15, 30, 25, 40, 35, 50, 45, 60]
})

# Mise en page de l'application
app.layout = html.Div(children=[
    html.Div([
        html.Label("Date de début"),
        dcc.DatePickerSingle(
            id='start-date-picker',
            min_date_allowed=df['date'].min(),
            max_date_allowed=df['date'].max(),
            date=df['date'].min(),
        ),
        html.Label("Date de fin"),
        dcc.DatePickerSingle(
            id='end-date-picker',
            min_date_allowed=df['date'].min(),
            max_date_allowed=df['date'].max(),
            date=df['date'].max(),
        )
    ], style={'width': '30%', 'display': 'inline-block', 'padding': '20px'}),

    html.Div([
        dcc.Graph(id='graph')
    ], style={'width': '60%', 'display': 'inline-block'}),
])

# Callback pour mettre à jour le graphique en fonction des dates sélectionnées
@app.callback(
    Output('graph', 'figure'),
    [Input('start-date-picker', 'date'),
     Input('end-date-picker', 'date')]
)
def update_graph(start_date, end_date):
    # Convertir les dates en format datetime
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

    # Filtrer les données selon les dates sélectionnées
    filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

    # Créer la figure avec Plotly
    fig = px.line(filtered_df, x="date", y="value", title="Évolution des valeurs")

    return fig

# Lancer l'application
if __name__ == '__main__':
    app.run_server(debug=True)
