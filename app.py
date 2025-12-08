import streamlit as st
import json
import pandas as pd
from backend import parse_schedule, generate_ics_file

st.set_page_config(page_title="Chaos Manager", page_icon="⚡", layout="wide")

# --- CSS POUR FLOUTER (EFFET LOCK) ---
st.markdown("""
<style>
.blur-text {
    color: transparent;
    text-shadow: 0 0 8px rgba(0,0,0,0.5);
    user-select: none;
}
.locked-box {
    border: 1px solid #FF4B4B;
    background-color: #FF4B4B1A;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR : LE PROFILAGE ---
with st.sidebar:
    st.header("🧠 Tes Préférences")
    st.write("Dis-moi comment tu fonctionnes.")
    
    wake_up = st.time_input("Je me lève à :", value=None)
    
    intensity = st.select_slider(
        "Durée max de concentration (Deep Work) :",
        options=["30 min (Pomodoro)", "1h", "2h", "4h (Mode Guerrier)"],
        value="2h"
    )
    
    distribution = st.radio(
        "Répartition de l'effort :",
        ["⚡ Gros blocs (Libre ensuite)",
         "💧 Étaler (Régularité)"]
    )
    
    st.divider()
    st.caption("L'IA adapte la stratégie à ces paramètres.")

# --- MAIN PAGE ---
st.title("⚡ Chaos Manager")
st.subheader("L'IA qui range ta vie à ta place.")

user_input = st.text_area(
    "1. Raconte ta semaine en vrac :", 
    height=150, 
    placeholder="Ex: J'ai un partiel de physique vendredi, je dois réviser 10h au total. Je veux faire du sport 3x cette semaine le soir..."
)

if st.button("Générer mon Planning", type="primary"):
    if not user_input:
        st.warning("Remplis d'abord tes contraintes !")
    else:
        with st.spinner("Analyse de ton profil psychologique et temporel..."):
            try:
                # Packaging des préférences
                prefs = {
                    "intensity": intensity,
                    "distribution": distribution,
                    "wake_up": str(wake_up) if wake_up else "08:00"
                }
                
                # APPEL BACKEND
                raw_response = parse_schedule(user_input, prefs)
                
                # NETTOYAGE
                cleaned = raw_response.replace("```json", "").replace("```", "").strip()
                data_obj = json.loads(cleaned)
                
                planning_data = data_obj.get("planning", [])
                # On garde le message pour nous (on ne l'affiche pas)
                
                # --- AFFICHAGE ---
                
                # 1. Le Tableau (GRATUIT)
                st.subheader("📅 Aperçu du Planning")
                if planning_data:
                    df = pd.DataFrame(planning_data)
                    st.dataframe(
                        df[["titre", "start_iso", "end_iso", "categorie"]],
                        use_container_width=True,
                        hide_index=True
                    )
                
                # 2. L'Analyse (VERROUILLÉE)
                st.markdown("---")
                col_lock, col_buy = st.columns([1.5, 1])
                
                with col_lock:
                    st.warning("🔒 **Analyse Stratégique Verrouillée**")
                    st.markdown("""
                    L'IA a généré une **explication psychologique** de ce planning basée sur ton profil :
                    - *Pourquoi ces horaires précis ?*
                    - *Comment gérer ton énergie "Mode Guerrier" ?*
                    - *La justification des blocs de repos.*
                    """)
                    # Effet visuel de texte flouté pour teaser
                    st.markdown('<p class="blur-text">Voici pourquoi j ai placé le sport le mardi soir car ton pic de dopamine est...</p>', unsafe_allow_html=True)
                
                with col_buy:
                    st.header("Débloquer tout")
                    st.markdown("""
                    Obtiens le **Pack Organisation** complet :
                    1. 📤 Le fichier **.ics** (Google/Apple Agenda).
                    2. 🧠 Le **Rapport d'Analyse** complet (PDF/Texte).
                    3. 💡 Mes conseils personnalisés.
                    """)
                    
                    # TON LIEN STRIPE ICI
                    st.link_button(
                        "🔓 DÉBLOQUER MAINTENANT (9.90€)", 
                        "https://buy.stripe.com/TON_LIEN_ICI"
                    )
                    st.caption("Paiement unique. Satisfait ou remboursé.")

            except Exception as e:
                st.error(f"Oups, erreur technique : {e}")