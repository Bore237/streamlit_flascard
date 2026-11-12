import streamlit as st

st.set_page_config(layout='wide')
st.title('Configuration', text_alignment='center')

## -------------------------- Gestion des données globales ----------------
# Sécurité pour s'assurer que les éléments de session existent
if "db" not in st.session_state:
    st.warning("Commencer pas lancer la parge Flashcards")
    st.stop() # Arrête l'exécution si on accède directement à la page sans passer par le main

if "confirm_delete_theme" not in st.session_state:
    st.session_state.confirm_delete_theme = False

# Fonction pour rafraîchir les données en session
def refresh_data():
    df_theme = st.session_state.db.get_from_db('themes')
    st.session_state.theme_dict = {
        name: id for id, name in zip(df_theme['id_theme'], df_theme['theme'])
    }

# Initialisation du dictionnaire des thèmes si vide
if "theme_dict" not in st.session_state or not st.session_state.theme_dict:
    refresh_data()

## -------------------------- Gestion des themes ------------
st.markdown("### Gérer les thèmes")

col1, _, col2 = st.columns((2, 1, 2))
with col1:
    with st.form("add_theme", clear_on_submit=True):
        val = st.text_input("Ajouter le theme")
        submitted = st.form_submit_button('Ajouter le thème')
        if submitted:
            if val:
                st.session_state.db.add_on_db('themes', theme=val)
                refresh_data()
                st.success("Thème ajouté avec succès !")
                st.rerun()
            else:
                st.warning("Veuillez entrer un nom de thème.")

with col2:
    with st.container(border=True):
        themes_keys = list(st.session_state.get("theme_dict", {}).keys())
        if themes_keys:
            theme_to_delete = st.selectbox("Nom du thème à supprimer", themes_keys, key="select_theme_delete")

            if st.button("Supprimer le theme", key="btn_init_del_theme"):
                st.session_state.confirm_delete_theme = True

            if st.session_state.confirm_delete_theme:
                st.warning(f"Voulez-vous vraiment supprimer le thème '{theme_to_delete}' et toutes ses cartes ?")
                col_y, col_n = st.columns(2)
                with col_y:
                    if st.button("Oui, confirmer", key="confirm_del_theme_yes"):
                        id_theme = st.session_state.theme_dict[theme_to_delete]
                        st.session_state.db.delete_id('themes', id=id_theme)
                        refresh_data()
                        st.session_state.confirm_delete_theme = False
                        st.success(f"Thème '{theme_to_delete}' supprimé avec succès !")
                        st.rerun()
                with col_n:
                    if st.button("Annuler", key="confirm_del_theme_no"):
                        st.session_state.confirm_delete_theme = False
                        st.rerun()
        else:
            st.info("Aucun thème disponible.")

st.divider()

##-------------------------- Gérer flashcard ----------------
st.markdown("### Ajouter une nouvelle flashcard")

with st.container(border=True):
    with st.form("add_card_form", clear_on_submit=True):
        question = st.text_input("Question", key="new_card_q")
        reponse = st.text_input("Réponse", key="new_card_r")
        
        themes_list = list(st.session_state.theme_dict.keys())
        if themes_list:
            theme_choice = st.selectbox("Thème", themes_list, key="new_card_theme")
            submitted_card = st.form_submit_button('Ajouter la flashcard')
            
            if submitted_card:
                if question and reponse and theme_choice:
                    st.session_state.db.add_on_db(
                        'cards', 
                        question=question, 
                        reponse=reponse,
                        probabilite=0.5, 
                        id_theme=st.session_state.theme_dict[theme_choice]
                    )
                    st.success("Flashcard ajoutée avec succès !")
                    st.rerun()
                else:
                    st.warning("Veuillez remplir tous les champs.")
        else:
            st.warning("Veuillez d'abord créer un thème.")

st.divider()

##-------------------------- Afficher / Modifier / Supprimer les flashcards par thème ----------------
st.markdown("### Afficher et Gérer les flashcards par thème")

themes_list_display = list(st.session_state.theme_dict.keys())
if themes_list_display:
    theme_display = st.selectbox("Nom du thème à afficher", themes_list_display, key="select_theme_display")

    with st.container(border=True):
        df_cards_all = st.session_state.db.get_from_db('cards')
        id_query = st.session_state.theme_dict[theme_display]
        df_filter = df_cards_all.query('id_theme == @id_query')
        
        if df_filter.empty:
            st.info("Aucune flashcard pour ce thème.")
        else:
            for _, row in df_filter.reset_index().iterrows():
                card_id = row['id_card']
                
                st.html(f"<strong>Question</strong>: {row['question']}")
                st.html(f"<strong>Réponse</strong>: {row['reponse']}")
                
                # Gestion de la modification en mode édition inline
                edit_key = f"edit_mode_{card_id}"
                if edit_key not in st.session_state:
                    st.session_state[edit_key] = False

                col_btn1, col_btn2, _ = st.columns([1, 1, 4])
                with col_btn1:
                    if st.button("Modifier", key=f"btn_update_{card_id}"):
                        st.session_state[edit_key] = not st.session_state[edit_key]
                        st.rerun()
                with col_btn2:
                    if st.button("Supprimer", key=f"btn_delete_{card_id}"):
                        st.session_state.db.delete_id('cards', id=card_id)
                        st.success("Carte supprimée avec succès !")
                        st.rerun()

                # Formulaire de mise à jour s'affiche si l'utilisateur a cliqué sur Modifier
                if st.session_state[edit_key]:
                    with st.form(key=f"form_update_{card_id}"):
                        new_q = st.text_input("Modifier la question", value=row['question'])
                        new_r = st.text_input("Modifier la réponse", value=row['reponse'])
                        if st.form_submit_button("Enregistrer les modifications"):
                            # Supposons que votre classe DatabaseRequest gère une méthode update ou équivalente, 
                            # ou exécutez votre requête SQL de mise à jour ici :
                            st.session_state.db.update_db('cards', id=card_id, question=new_q, reponse=new_r)
                            st.session_state[edit_key] = False
                            st.success("Carte mise à jour !")
                            st.rerun()
                st.divider()
else:
    st.info("Aucun thème disponible pour afficher les cartes.")