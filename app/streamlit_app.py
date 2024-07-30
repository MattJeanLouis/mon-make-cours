import streamlit as st
import requests
import time
import threading
import base64
import os

API_URL = "http://localhost:8000"

def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Télécharger {file_label}</a>'
    return href

def get_status_color(status):
    if status == "en_attente":
        return "🟡"
    elif status == "en_cours":
        return "🟠"
    elif status == "terminé":
        return "🟢"
    else:
        return "⚪"

def afficher_cours(cours_id):
    response = requests.get(f"{API_URL}/cours/{cours_id}")
    if response.status_code == 200:
        cours = response.json()
        if cours['status'] == "terminé":
            sommaire = cours.get('sommaire', 'Sommaire non disponible')
            contenu = cours.get('contenu', 'Contenu non disponible')
            
            st.markdown("## Sommaire")
            st.markdown(sommaire)
            
            st.markdown("## Contenu")
            st.markdown(contenu)
        elif cours['status'] == "en_attente":
            st.info("Le cours est en attente de génération.")
        else:
            st.warning("Le cours est en cours de génération.")
    else:
        st.error("Cours non trouvé")

def main_page():
    st.title("Générateur de Cours")

    # Champ de saisie pour générer un nouveau cours
    theme = st.text_input("Entrez le thème du cours à générer :")
    if st.button("Générer le cours"):
        response = requests.post(f"{API_URL}/generer_cours/", json={"theme": theme})
        if response.status_code == 200:
            cours = response.json()
            st.success(f"Cours en cours de génération avec l'ID : {cours['id']}")
            time.sleep(2)  # Attendre 2 secondes
            st.rerun()  # Rafraîchir la page
        else:
            st.error("Erreur lors de la génération du cours")

    # Liste de tous les cours générés
    st.subheader("Cours générés")
    response = requests.get(f"{API_URL}/cours")
    if response.status_code == 200:
        cours_list = response.json()
        for cours in cours_list:
            status_color = get_status_color(cours['status'])
            if st.button(f"{status_color} Cours {cours['id']}: {cours['theme']}", key=cours['id']):
                st.session_state.page = "visualisation"
                st.session_state.selected_cours = cours['id']
                st.rerun()
    else:
        st.error("Erreur lors de la récupération de la liste des cours")

def visualisation_page():
    st.title("Visualisation du Cours")

    # Boutons en haut de la page
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Retour à la page principale"):
            st.session_state.page = "main"
            st.rerun()
    with col2:
        if st.button("Rafraîchir le contenu"):
            st.rerun()

    # Récupérer la liste des cours
    response = requests.get(f"{API_URL}/cours")
    if response.status_code == 200:
        cours_list = response.json()
        cours_options = {f"Cours {c['id']}: {c['theme']}": c['id'] for c in cours_list}
        
        # Créer le menu déroulant
        selected_cours = st.selectbox("Sélectionnez un cours", list(cours_options.keys()), 
                                      index=list(cours_options.values()).index(st.session_state.selected_cours) 
                                      if 'selected_cours' in st.session_state else 0)
        
        # Récupérer les détails du cours sélectionné
        cours_id = cours_options[selected_cours]
        cours_response = requests.get(f"{API_URL}/cours/{cours_id}")
        if cours_response.status_code == 200:
            cours = cours_response.json()
            if cours['status'] == "terminé":
                afficher_cours(cours_id)
                # Ajouter le bouton de téléchargement
                if 'fichier_path' in cours and cours['fichier_path']:
                    st.markdown(get_binary_file_downloader_html(cours['fichier_path'], 'le cours en format Markdown'), unsafe_allow_html=True)
            elif cours['status'] == "en_cours":
                st.warning("Le cours est en cours de génération. Veuillez patienter...")
                st.info("Vous pouvez rafraîchir la page pour voir si le cours est terminé.")
            elif cours['status'] == "en_attente":
                st.info("Le cours est en attente de génération. La génération commencera bientôt.")
            else:
                st.error("Statut du cours inconnu.")
        else:
            st.error("Erreur lors de la récupération des détails du cours")
    else:
        st.error("Erreur lors de la récupération de la liste des cours")

def update_cours_status():
    while True:
        response = requests.get(f"{API_URL}/cours")
        if response.status_code == 200:
            cours_list = response.json()
            for cours in cours_list:
                if cours['status'] != "terminé":
                    st.session_state[f"cours_{cours['id']}_status"] = cours['status']
        time.sleep(5)  # Mettre à jour toutes les 5 secondes

# Ajouter cette ligne après l'initialisation de st.session_state
if 'update_thread' not in st.session_state:
    st.session_state.update_thread = threading.Thread(target=update_cours_status)
    st.session_state.update_thread.start()

# Initialisation de la session state
if 'page' not in st.session_state:
    st.session_state.page = "main"

# Navigation entre les pages
if st.session_state.page == "main":
    main_page()
elif st.session_state.page == "visualisation":
    visualisation_page()