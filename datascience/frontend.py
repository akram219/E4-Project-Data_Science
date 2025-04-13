import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Prédiction Électrique", layout="centered")

st.title('🔌 Prédiction de Consommation Électrique')

st.subheader('📤 Téléchargez un fichier CSV ou Excel')
uploaded_file = st.file_uploader("Choisir un fichier", type=["csv", "xlsx"])

model_choice = st.radio("Choisir le modèle de prédiction :", ["SARIMAX", "AR"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)

        st.success("✅ Fichier chargé avec succès")
        st.dataframe(df.head())

        if st.button(f"🚀 Prédire avec {model_choice}"):
            with st.spinner("Envoi du fichier à l'API..."):
                api_url = f"http://127.0.0.1:5000/predict/{model_choice.lower()}"
                response = requests.post(api_url, files={"file": (uploaded_file.name, uploaded_file.getvalue())})

            if response.status_code == 200:
                result = response.json()["prediction"]
                st.success("✅ Prédiction réussie")

                st.subheader("📂 Résultats")
                st.write(f"Nombre d'observations : {result['metadata']['nb_observations']}")
                st.write(f"Période : {result['metadata']['periode']}")
                st.write(f"Dernière consommation : {result['derniere_valeur']}")
                st.write(f"Prochaine prédiction : {result['prochaine_prediction']}")

                stats = result['statistiques']
                st.markdown("**📊 Statistiques :**")
                st.write(f"- Moyenne : {stats['moyenne']}")
                st.write(f"- Max : {stats['max']}")
                st.write(f"- Min : {stats['min']}")
                st.write(f"- MSE : {stats['mse']}")

                sample_df = pd.DataFrame(result['data_sample'])
                st.markdown("### 🔍 Échantillon de données")
                st.dataframe(sample_df)

                # Courbe
                st.markdown("### 📈 Courbe de consommation et prédiction")
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=sample_df['DateTime'],
                    y=sample_df['Consommation'],
                    mode='lines',
                    name='Consommation réelle',
                    line=dict(color='blue')
                ))
                fig.add_trace(go.Scatter(
                    x=sample_df['DateTime'],
                    y=sample_df['Prediction'],
                    mode='lines',
                    name=f'Prédiction {model_choice}',
                    line=dict(color='red', dash='dot')
                ))
                fig.update_layout(
                    xaxis_title="DateTime",
                    yaxis_title="Consommation",
                    legend_title="Légende",
                    template="plotly_white"
                )
                st.plotly_chart(fig, use_container_width=True)

            else:
                st.error(f"❌ Erreur de prédiction : {response.json().get('error')}")

    except Exception as e:
        st.error(f"❌ Erreur lors du traitement du fichier : {e}")
