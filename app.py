import streamlit as st
import json
import pandas as pd
from backend import parse_schedule, generate_ics_file # On importe les deux moteurs

# 1. CONFIGURATION
st.set_page_config(page_title="Chaos Manager", page_icon="⚡", layout="centered")

# 2. TITRE
st.title("⚡ Chaos Manager")
st.markdown("### Transforme ton vrac mental en planning structuré.")

# 3. ZONE DE SAISIE
user_input = st.text_area(
    "Colle tes impératifs ici :", 
    height=150, 
    placeholder="Ex: Dentiste mardi 14h, Gym 3 fois par semaine, Rendre devoir physique vendredi..."
)

# 4. LE DÉCLENCHEUR
if st.button("Générer mon Planning", type="primary"):
    if not user_input:
        st.warning("Écris quelque chose d'abord !")
    else:
        with st.spinner("L'IA réfléchit..."):
            try:
                # --- ÉTAPE 1 : GÉNÉRATION IA ---
                raw_response = parse_schedule(user_input)
                
                # Nettoyage du JSON
                cleaned_response = raw_response.replace("```json", "").replace("```", "").strip()
                data = json.loads(cleaned_response)
                
                # Succès
                st.success(f"C'est fait ! {len(data)} événements trouvés.")
                
                # Affichage Tableau
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # --- ÉTAPE 2 : EXPORT ICS (Le Bouton Magique) ---
                st.markdown("---")
                st.subheader("🗓️ Exporter vers mon Agenda")
                
                ics_content = generate_ics_file(data)
                
                if ics_content:
                    st.download_button(
                        label="📥 Télécharger le fichier .ics (Google/Outlook/Apple)",
                        data=ics_content,
                        file_name="mon_planning_chaos.ics",
                        mime="text/calendar"
                    )
                    st.info("💡 Mode d'emploi : Clique sur le bouton, ouvre le fichier téléchargé, et valide l'ajout à ton calendrier.")
                else:
                    st.error("Erreur lors de la création du fichier calendrier.")
                
            except Exception as e:
                st.error(f"Erreur critique : {e}")