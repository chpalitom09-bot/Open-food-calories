import streamlit as st
import json
import os

# Configuration de la page
st.set_page_config(page_title="FoodCal Python", page_icon="🥗")

# Fonction pour charger les données
def load_data():
    # On cherche le fichier dans le dossier data
    path = "data/food.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

data = load_data()

# Interface Streamlit
st.title("🥗 FoodCal - Recherche Python")
st.write(f"Base de données : {len(data)} aliments chargés.")

# Barre de recherche
query = st.text_input("Rechercher un aliment...", "").lower()

if query:
    # Filtrage
    results = [
        f for f in data 
        if query in f['name'].lower() or query in f['english_name'].lower()
    ]
    
    if results:
        for f in results:
            # Affichage style "carte"
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"### {f['emoji']} {f['name']}")
                    st.caption(f"Nom anglais : {f['english_name']}")
                with col2:
                    st.metric("Calories", f"{f['kcal_per_100g']} kcal")
                st.divider()
    else:
        st.warning("Aucun résultat trouvé.")
else:
    st.info("Entrez un nom d'aliment pour commencer.")
