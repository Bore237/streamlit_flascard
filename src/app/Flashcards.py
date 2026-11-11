import streamlit as st
from flashcards.database import DatabaseRequest
from flashcards.stat import StatTools
import plotly.express as px
from flashcards.logger import get_log
import random

logger = get_log(__name__)

# Get element on database
flascards = DatabaseRequest('flashcards.db')
stat = StatTools('flashcards.db')

@st.cache_resource
def get_data():
    df_theme = flascards.get_from_db('themes')
    total_card = flascards.count('cards')
    df_cards_all = flascards.get_from_db('cards')
    return df_theme, total_card, df_cards_all

df_theme, total_card, df_cards_all = get_data()
theme_dict = {name: id for id, name in zip(list(df_theme['id_theme']), list(df_theme['theme']))}

## Start design
st.write("##")
st.set_page_config(page_title="borel_flashcard", layout="wide")
st.title("Flascard Application")
st.divider()

## ------------------------- sidebar--------------------------
st.sidebar.markdown(f"#### Nombre total de cartes: {total_card}")
st.sidebar.markdown(f"#### Repartition des thèmes les plus representer", text_alignment='center')

### ----------------------- Pie Plot ---------------------
val =  st.sidebar.number_input("Nombre de Theme choisir",min_value=3,  max_value= len(df_theme['theme'].unique()),format="%d")
@st.cache_resource
def display_theme_pie(val):
    cards_count = df_cards_all['id_theme'].value_counts().sort_values().iloc[:val]
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

display_theme_pie(val)

### ------------------------------ Select theme ------------------
theme_select = st.sidebar.selectbox("Selectioner un Theme", theme_dict.keys())

@st.cache_resource
def get_card(theme_select):
    df_cards = flascards.get_from_db('cards', id_theme=theme_dict[theme_select])
    return df_cards

df_cards = get_card(theme_select)
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

valid_btn = False
 
## ---------------------------- Card ---------------------
with st.container(border=True):
    st.markdown(f'### Theme: {theme_select}')
    st.markdown("#### Question:")
    with st.container(border=True):
        st.write(cards_select['question'])

    anwser = st.text_area("votre réponse")
    c1, _, c2 = st.columns((2,1,2))
    with c1:
        valid_btn = st.button("Valider")
    with c2:
        st.feedback("faces")

if valid_btn:
    with st.container() as ctn:
        st.markdown("### Votre réponse vs La bonne réponse")
        col1, col2 = st.columns(2, gap='medium')
        with col1:
            st.write("##### Votre réponse")
            # Utilisation d'une div stylisée proprement
            st.markdown(
                f"""<div style="background-color: #fff3cd; color: black; border: 1px solid #ffeeba; padding: 10px; border-radius: 5px;">
                    {anwser}
                </div>""",
                unsafe_allow_html=True
            )
            
        with col2:
            st.write("##### La bonne réponse")
            st.markdown(
                f"""<div style="background-color: #d4edda; color: black; border: 1px solid #c3e6cb; padding: 10px; border-radius: 5px;">
                    {cards_select['reponse']}
                </div>""",
                unsafe_allow_html=True
            )
    st.divider()
    st.markdown("### Avez-vous correctement répondu ?")
    id_card = cards_select["id_card"]
    col1, col2 = st.columns(2, gap='medium')

    with col1:
        yes_confirm = st.button("Oui")
    with col2:
        no_confirm = st.button("Non")

    if yes_confirm:
        is_correct = True
        stat.update_stats(is_correct)
        stat.update_card_probability(id_card, is_correct)

    if yes_confirm:
        is_correct = False
        stat.update_stats(is_correct)
        stat.update_card_probability(id_card, is_correct)
