import streamlit as st
import json
import pandas as pd
from backend import parse_schedule, generate_ics_file

# --- CONFIGURATION DU SITE ---
st.set_page_config(page_title="Chaos Manager", page_icon="⚡", layout="centered")

# --- HEADER PRO ---
st.title("⚡ Chaos Manager")
st.subheader("L'IA qui range ta vie à ta place.")
st.info("💡 **Offre de Lancement :** Teste l'outil gratuitement ci-dessous. Pour exporter vers Google/Apple Agenda, débloque la version complète.")

# --- ZONE DE DÉMO ---
user_input = st.text_area(
    "1. Raconte ta semaine en vrac (Audio ou Texte) :", 
    height=150, 
    placeholder="Exemple : J'ai cours de physique tous les mardis matin, je dois aller au MMA le jeudi à 19h, et rappelle-moi de bosser mon projet ce week-end..."
)

if st.button("🔍 Prévisualiser mon Planning", type="primary"):
    if not user_input:
        st.warning("Écris quelque chose pour tester la magie !")
    else:
        with st.spinner("Analyse du chaos en cours..."):
            try:
                # Appel IA
                raw_response = parse_schedule(user_input)
                cleaned = raw_response.replace("```json", "").replace("```", "").strip()
                data = json.loads(cleaned)
                
                # PREUVE VISUELLE (Le "Wow")
                st.success(f"✅ Analyse réussie ! {len(data)} événements détectés.")
                df = pd.DataFrame(data)
                
                # On affiche un tableau propre
                st.dataframe(
                    df[["titre", "start_iso", "end_iso", "categorie"]],
                    column_config={
                        "titre": "Événement",
                        "start_iso": "Début",
                        "end_iso": "Fin",
                        "categorie": "Type"
                    },
                    use_container_width=True,
                    hide_index=True
                )
                
                # --- LE PÉAGE (Call to Action) ---
                st.markdown("---")
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown("""
                    ### 🔓 Débloquer mon fichier Agenda
                    Pour ajouter ces événements directement dans **Google Agenda, Apple ou Outlook** :
                    1. Cliquez sur le bouton pour régler l'accès (**9.90€** - Paiement Sécurisé Stripe).
                    2. Envoyez-moi votre texte par mail (indiqué après paiement).
                    3. Recevez votre fichier `.ics` prêt à l'emploi sous 24h.
                    """)
                
                with col2:
                    # REMPLACE L'URL CI-DESSOUS PAR TON LIEN STRIPE
                    st.link_button(
                        "💳 ACHETER (9.90€)", 
                        "https://buy.stripe.com/test_aFa4gAdYxcMBbCIbZOd7q00"
                    )
                    
            except Exception as e:
                st.error(f"Oups, petite erreur de lecture. Essaie de reformuler : {e}")

# --- PIED DE PAGE ---
st.markdown("---")
st.caption("🔒 Service sécurisé. Satisfait ou remboursé. Développé par Retro Lab.")