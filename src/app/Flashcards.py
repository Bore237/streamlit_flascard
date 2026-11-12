import streamlit as st
from flashcards.database import DatabaseRequest
from flashcards.stat import StatTools
import plotly.express as px
from flashcards.logger import get_log
import random
from pathlib import Path

# Configuration de la page (doit être la première commande st.*)
st.set_page_config(page_title="borel_flashcard", layout="wide")

##---------------- Initialisation de la session --------------
if "run_get_data" not in st.session_state:
    st.session_state.run_get_data = False

if "theme_dict" not in st.session_state:
    st.session_state.theme_dict = {}

if "db" not in st.session_state:
    st.session_state.db = DatabaseRequest('flashcards.db')
    df_theme = st.session_state.db.get_from_db('themes')
    #load json file if database is empty
    if df_theme.empty:
        st.session_state.db.load_db(json_path=Path("data/flashcards.json"))
        st.rerun()

if "db_stat" not in st.session_state:
    st.session_state.db_stat = StatTools('flashcards.db')

if "confirm_result" not in st.session_state:
    st.session_state.confirm_result = False

if "answer" not in st.session_state:
    st.session_state.answer = None

if "current_card" not in st.session_state:
    st.session_state.current_card = None

logger = get_log(__name__)

## ------------------------ Données globales ------------------
@st.cache_resource
def get_data():
    df_theme = st.session_state.db.get_from_db('themes')
    total_card = st.session_state.db.count('cards')
    df_cards_all = st.session_state.db.get_from_db('cards')
    return df_theme, total_card, df_cards_all

df_theme, total_card, df_cards_all = get_data()

st.session_state.theme_dict = dict(zip(df_theme['theme'], df_theme['id_theme']))

## Start design
data_version = st.write("##")
st.title("Flashcard Application")
st.divider()

## ------------------------- sidebar--------------------------
st.sidebar.markdown(f"#### Nombre total de cartes: {total_card}")
st.sidebar.markdown(f"#### Repartition des thèmes les plus representer")

### ----------------------- Pie Plot ---------------------
val = st.sidebar.number_input("Nombre de Theme choisir", min_value=3, max_value=len(df_theme['theme'].unique()), format="%d", value=min(3, len(df_theme['theme'].unique())))

def display_theme_pie(val):
    # Trie par ordre croissant et on garde les 'val' premiers
    cards_count = df_cards_all['id_theme'].value_counts().reset_index()
    cards_count.columns = ['id_theme', 'count']
    cards_count = cards_count.sort_values('count', ascending=True).head(val)
    temp = dict(zip(df_theme['id_theme'], df_theme['theme']))
    cards_count['theme'] = cards_count['id_theme'].map(temp)

    fig = px.pie(cards_count,  names='theme', values='count', title="Répartition des cartes par thème", hole=0.1)
    fig.update_layout(
        legend_title="Thèmes",
        legend=dict(orientation="v", yanchor="middle", y=-0.1, xanchor="center", x=0.5),
    )
    st.sidebar.plotly_chart(fig)

display_theme_pie(val)

date = st.sidebar.date_input("Choisir une Date")
date_str = date.strftime("%Y-%m-%d")

### ------------------------------ Select theme ------------------
theme_select = st.sidebar.selectbox("Selectioner un Theme", list(st.session_state.theme_dict.keys()))

# Si on change de thème, on force le renouvellement de la carte courante
if "last_theme" not in st.session_state or st.session_state.last_theme != theme_select:
    st.session_state.last_theme = theme_select
    st.session_state.current_card = None
    st.session_state.confirm_result = False

def get_card(theme_name):
    return st.session_state.db.get_from_db('cards', id_theme=st.session_state.theme_dict[theme_name])

df_cards = get_card(theme_select)

# Sélection de la carte uniquement si aucune n'est active en session
if st.session_state.current_card is None:
    if not df_cards.empty:
        prob = random.random()
        cards = df_cards.query('probabilite > @prob')
        if cards.empty:
            idx = random.randint(0, len(df_cards) - 1) 
            st.session_state.current_card = df_cards.reset_index().iloc[idx].to_dict()
        else:
            idx = random.randint(0, len(cards) - 1) 
            st.session_state.current_card = cards.reset_index().iloc[idx].to_dict()

## ---------------------------- Card ---------------------
with st.container(border=True):
    st.markdown(f'### Theme: {theme_select}')
    st.markdown("#### Question:")
    
    if st.session_state.current_card is not None:
        cards_select = st.session_state.current_card
        id_card = cards_select["id_card"]

        st.markdown(
            f"""<div style="background-color: #cce5ff; border: 1px solid #b8daff; padding: 10px; border-radius: 5px; margin-bottom: 15px; color: #004085;">
                {cards_select['question']}
            </div>""",
            unsafe_allow_html=True
        )

        if st.session_state.confirm_result:
            st.markdown("### Votre réponse vs La bonne réponse")
            col1, col2 = st.columns(2, gap='medium')
            with col1:
                st.write("##### Votre réponse")
                st.markdown(f"""<div style="background-color: #fff3cd; color: black; border: 1px solid #ffeeba; padding: 10px; border-radius: 5px;">
                        {st.session_state.answer}
                    </div>""",
                    unsafe_allow_html=True
                )
                
            with col2:
                st.write("##### La bonne réponse")
                st.markdown(f"""<div style="background-color: #d4edda; color: black; border: 1px solid #c3e6cb; padding: 10px; border-radius: 5px;">
                        {cards_select['reponse']}
                    </div>""",
                    unsafe_allow_html=True
                )

            st.divider()
            st.markdown("### Avez-vous correctement répondu ?")
            
            col1, col2 = st.columns(2, gap='medium')
            with col1:
                if st.button("Oui", key="btn_oui"):
                    st.session_state.db_stat.update_stats(True, date_str)
                    st.session_state.db_stat.update_card_probability(id_card, True)
                    st.session_state.confirm_result = False
                    st.session_state.current_card = None # Force le tirage d'une nouvelle carte au prochain tour
                    st.rerun()
            with col2:
                if st.button("Non", key="btn_non"):
                    st.session_state.db_stat.update_stats(False, date_str)
                    st.session_state.db_stat.update_card_probability(id_card, False)
                    st.session_state.confirm_result = False
                    st.session_state.current_card = None # Force le tirage d'une nouvelle carte au prochain tour
                    st.rerun()
        
        else:
            # Utilisation de st.text_area avec une clé de session pour persister la valeur
            st.session_state.answer = st.text_area("votre réponse", value=st.session_state.answer or "")
            if st.button("Valider", key="btn_valider"):
                st.session_state.confirm_result = True
                st.rerun()
    else:
        st.warning("Aucune carte ne correspond à ce thème.")