import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="SARIMAX Prédiction", layout="centered")

st.title('🔌 Prédiction de Consommation Électrique avec SARIMAX')

st.subheader('📤 Téléchargez un fichier CSV ou Excel')
uploaded_file = st.file_uploader("Choisir un fichier", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        
        st.success("Fichier chargé avec succès ✅")
        st.write("Aperçu des données :")
        st.dataframe(df.head())

        if st.button('🚀 Effectuer la prédiction SARIMAX'):
            with st.spinner("Envoi du fichier à l'API..."):
                api_url = "http://127.0.0.1:5000/predict/sarimax"
                response = requests.post(api_url, files={"file": (uploaded_file.name, uploaded_file.getvalue())})

            if response.status_code == 200:
                data = response.json()
                st.success("✅ Prédiction réussie")

                for filename, result in data.items():
                    st.subheader(f"📂 Résultats pour : {filename}")
                    st.write(f"Nombre d'observations : {result['metadata']['nb_observations']}")
                    st.write(f"Période des données : {result['metadata']['periode']}")
                    st.write(f"Dernière valeur de consommation : {result['derniere_valeur']}")
                    st.write(f"Prochaine prédiction : {result['prochaine_prediction']}")

                    stats = result['statistiques']
                    st.markdown("**📊 Statistiques :**")
                    st.write(f"- Moyenne : {stats['moyenne']}")
                    st.write(f"- Max : {stats['max']}")
                    st.write(f"- Min : {stats['min']}")
                    st.write(f"- MSE : {stats['mse']}")

                    if "avertissements" in result:
                        st.warning("⚠️ Avertissements")
                        for k, v in result["avertissements"].items():
                            st.write(f"- {k} : {v}")

                    st.write("🔍 Échantillon des données prédites :")
                    sample_df = pd.DataFrame(result['data_sample'])
                    st.dataframe(sample_df)

                    # Ajout du graphique
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
                        name='Prédiction SARIMAX',
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
