import streamlit as st
from flashcards.database import DatabaseRequest
import plotly.express as px
from flashcards.logger import get_log
import random

logger = get_log(__name__)

# Get element on database
flascards = DatabaseRequest('flashcards.db')
df_theme = flascards.get_from_db('themes')
theme_dict = {name: id for id, name in zip(list(df_theme['id_theme']), list(df_theme['theme']))}
total_card = flascards.count('cards')

## Start design
st.write("##")
st.set_page_config(page_title="borel_flashcard", layout="wide")
st.title("Flascard Application")
st.divider()

#sidebar
st.sidebar.markdown(f"#### Nombre total de cartes: {total_card}")
st.sidebar.markdown(f"#### Repartition des thèmes les plus representer", text_alignment='center')
df_cards = flascards.get_from_db('cards')

val =  st.sidebar.number_input("Nombre de Theme choisir",min_value=3,  max_value= len(df_theme['theme'].unique()),format="%d")
cards_count = df_cards['id_theme'].value_counts().sort_values().iloc[:val]
temp = {id: name for id, name in zip(list(df_theme['id_theme']), list(df_theme['theme']))}
labels = cards_count.index.map(temp)
fig = px.pie(cards_count, names=labels,
    title="Répartition des cartes par thème", hole=0.1)
fig.update_layout(legend_title="Thèmes",
    legend=dict(
        orientation="v", yanchor="middle", y=-0.1, xanchor="center", x=0.5
    ),
)
st.markdown(f"#### Les thèmes avec le plus de cartes")
st.sidebar.plotly_chart(fig)

theme_select = st.sidebar.selectbox("Selectioner un Theme", theme_dict.keys())
df_cards = flascards.get_from_db('cards', id_theme=theme_dict[theme_select])


prob = random.random()
cards = df_cards.query('probabilite > @prob')
if cards.empty:
    if df_cards.empty:
        logger.warning("Aucune card ne correcpond a ce thème")
    else:
        idx = random.randint(0, len(df_cards) -1) 
        cards_select = df_cards.reset_index().iloc[idx, :]
else:
   idx = random.randint(0, len(cards) -1) 
   cards_select = cards.reset_index().iloc[idx, :] 

## Card
with st.container(border=True):
    st.markdown(f'### Theme: {theme_select}')
    st.markdown("#### Question:")
    with st.container(border=True):
        st.write(cards_select['question'])
    st.text_area("votre réponse")
    valid_btn = st.button("Valider")

if valid_btn:
    pass