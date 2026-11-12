import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(layout='wide')

# Sécurité pour s'assurer que les éléments de session existent
if "db" not in st.session_state:
    st.warning("Commencer pas lancer la parge Flashcards")
    st.stop() # Arrête l'exécution si on accède directement à la page sans passer par le main

df_stats = st.session_state.db.get_from_db('stats')

st.write("##")
# Correction de l'argument text_alignment (souvent géré via markdown ou du CSS externe)
st.title("Vos statistiques")
st.divider()

if df_stats.empty:
    st.info("Aucune statistique disponible pour le moment. Répondez à quelques flashcards !")
else:
    st.markdown("### Évolution des réponses correctes et incorrectes par jour")
    df_stats['date'] = pd.to_datetime(df_stats['date'])
    df_stats = df_stats.sort_values('date')

    # Tracé du graphique linéaire
    plot1 = px.line(
        df_stats, 
        x='date', 
        y=["bonnes_reponses", "mauvaises_reponses"],
        labels={"value": "Nombre de réponses", "date": "Date", "variable": "Type de réponse"},
        color_discrete_map={"Bonnes réponses": "blue", "Mauvaises réponses": "red"}
    )
    st.plotly_chart(plot1, use_container_width=True) 

    st.divider()

    # Si votre table 'stats' stocke les totaux par jour, faisons la somme globale pour le pie chart
    total_bonnes = df_stats["bonnes_reponses"].sum()
    total_mauvaises = df_stats["mauvaises_reponses"].sum()

    st.markdown("### Répartition globale des réponses")

    # Création d'un DataFrame ou dict propre pour le camembert global
    import pandas as pd
    df_pie = pd.DataFrame({
        "Type": ["Bonnes réponses", "Mauvaises réponses"],
        "Total": [total_bonnes, total_mauvaises]
    })

    plot2 = px.pie(
        df_pie, 
        names="Type", 
        values="Total", 
        hole=0.3,
        color="Type",
        color_discrete_map={"Bonnes réponses": "green", "Mauvaises réponses": "red"}
    )
    st.plotly_chart(plot2, use_container_width=True)