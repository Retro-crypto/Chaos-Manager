import streamlit as st
import json
import pandas as pd
import plotly.express as px
from backend import parse_schedule, generate_ics_file

st.set_page_config(page_title="Chaos Manager V5", page_icon="🧠", layout="wide")

# --- CSS & STYLE ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .method-box { background-color: #1c202a; padding: 15px; border-radius: 10px; border-left: 4px solid #FF4B4B; margin-bottom: 20px; font-size: 14px;}
    .rpg-card { background: linear-gradient(135deg, #2b3042 0%, #161924 100%); border: 1px solid #444; border-radius: 15px; padding: 20px; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.4); }
    .archetype-title { color: #FF4B4B; font-size: 26px; font-weight: 800; text-transform: uppercase; margin-top: 10px;}
    .blur-text { filter: blur(5px); user-select: none; color: #888; opacity: 0.7; }
    .locked-section { border: 1px dashed #FF4B4B; padding: 20px; border-radius: 10px; background-color: #1e1111; text-align: center; margin-top: 20px;}
    .prompt-tag { background-color: #333; color: #00ff00; padding: 2px 8px; border-radius: 4px; font-family: monospace; font-size: 12px; margin-right: 5px;}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("🧠 Chaos Manager")
    st.caption("v5.0.1 (Beta)")
    st.markdown("---")
    st.info("💡 **Le Saviez-vous ?**\nLe modèle Big Five est le standard scientifique en psychométrie, bien plus fiable que le MBTI.")

# --- HEADER & PÉDAGOGIE ---
st.title("🧠 Chaos Manager : Expert Edition")
st.markdown("### L'ingénierie IA au service de ton organisation.")

with st.expander("ℹ️ Comment ça marche ? (Méthodologie)", expanded=False):
    st.markdown("""
    Contrairement aux agendas classiques, cet outil utilise le modèle des **Big Five (OCEAN)** pour adapter la journée à ta chimie cérébrale :
    * **O**uverture : Besoin de nouveauté vs Routine.
    * **C**onscience : Discipline naturelle vs Chaos.
    * **E**xtraversion : Besoin de stimulation sociale.
    * **A**gréabilité : Tendance à dire oui (et se faire bouffer).
    * **N**évrosisme : Sensibilité au stress et à l'imprévu.
    """)

st.write("Pour commencer, calibrons l'IA avec ton profil actuel.")

# --- FORMULAIRE D'AUTO-CALIBRATION (Honnête) ---
st.markdown("#### 1. Auto-Calibration Psychométrique")
st.caption("Ce n'est pas un diagnostic clinique, mais une calibration basée sur ton ressenti actuel.")

with st.form("psycho_form"):
    col1, col2 = st.columns(2)
    with col1:
        discipline = st.slider("Conscience / Discipline (Est-ce que tu finis ce que tu commences ?)", 0, 100, 40)
        stress = st.slider("Névrosisme / Stress (Ton niveau d'anxiété face à l'imprévu)", 0, 100, 60)
        energy = st.select_slider("Ton niveau d'Énergie ce matin :", options=["🧟 Zombie", "🔋 Faible", "⚡ Moyen", "🔥 Au Max"])
    
    with col2:
        openness = st.slider("Ouverture (Besoin de nouveauté vs Routine)", 0, 100, 70)
        social = st.slider("Extraversion (Besoin de voir des gens aujourd'hui)", 0, 100, 50)
    
    st.markdown("#### 2. La Mission")
    mission = st.text_area("Quels sont tes impératifs bruts ?", placeholder="Ex: Rendre projet Python, Sport ce soir, Appeler Maman...", height=100)
    
    submitted = st.form_submit_button("🚀 GÉNÉRER L'ANALYSE & LE PLANNING", type="primary", use_container_width=True)

# --- RÉSULTATS ---
if submitted:
    if not mission:
        st.warning("Donne-moi au moins une tâche !")
    else:
        with st.spinner("Simulation du cortex préfrontal... Application des matrices Big Five..."):
            # Appel Backend (Simulé)
            inputs = {"discipline": discipline, "mission": mission}
            data = json.loads(parse_schedule(inputs))
            
            # --- BLOC 1 : IDENTITÉ (GRATUIT) ---
            st.markdown("---")
            col_card, col_radar = st.columns([1, 1])
            
            with col_card:
                # Carte RPG
                st.markdown(f"""
                <div class="rpg-card">
                    <div style="font-size:12px; color:#FF4B4B; font-weight:bold;">✨ RARETÉ : {data.get('rarity')}</div>
                    <div class="archetype-title">{data.get('archetype')}</div>
                    <p style="font-style:italic; color:#aaa; margin-top:10px;">"{data.get('quote')}"</p>
                    <hr style="border-color:#444;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                        <span>⚔️ Atout :</span><span style="color:white; font-weight:bold;">{data.get('superpower')}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between;">
                        <span>💀 Faiblesse :</span><span style="color:white; font-weight:bold;">{data.get('kryptonite')}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            with col_radar:
                # Radar
                scores = data.get("scores", {})
                df_scores = pd.DataFrame(dict(r=list(scores.values()), theta=list(scores.keys())))
                fig = px.line_polar(df_scores, r='r', theta='theta', line_close=True, range_r=[0,100])
                fig.update_traces(fill='toself', line_color='#FF4B4B')
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
                st.plotly_chart(fig, use_container_width=True)

            # --- BLOC 2 : LE TEASING PLANNING (Semi-Gratuit) ---
            st.markdown("---")
            st.subheader("📅 Aperçu de ton Planning (Matinée)")
            st.caption("Voici comment l'IA structure ton démarrage pour contourner ta 'Faiblesse'.")
            
            planning = data.get("planning", [])
            # On affiche QUE les 2 premiers items
            if len(planning) > 0:
                df_free = pd.DataFrame(planning[:2]) # Les 2 premiers
                st.dataframe(df_free[["titre", "start_iso", "end_iso", "categorie"]], hide_index=True, use_container_width=True)
            
            # --- BLOC 3 : LE PAYWALL (La Valeur) ---
            st.markdown('<div class="locked-section">', unsafe_allow_html=True)
            st.write("🔒 **LA SUITE DE LA JOURNÉE EST VERROUILLÉE**")
            
            col_blur, col_pitch = st.columns([1.5, 1])
            with col_blur:
                st.markdown("#### Ce que tu manques :")
                # Faux planning flouté
                st.markdown('<div class="blur-text">14:00 - Deep Work Session 2 (Projet Critique)</div>', unsafe_allow_html=True)
                st.markdown('<div class="blur-text">16:00 - Gestion de crise (Admin & Mails)</div>', unsafe_allow_html=True)
                st.markdown('<div class="blur-text">18:00 - Routine de décompression Dopamine</div>', unsafe_allow_html=True)
                
                st.markdown("#### 🧠 Analyse Cognitive Exclusive :")
                st.markdown('<div class="blur-text">Ton score élevé en Névrosisme nécessite une approche spécifique. J ai supprimé les tâches anxiogènes du matin pour...</div>', unsafe_allow_html=True)

            with col_pitch:
                st.info("📦 **PACK COMPLET (9.90€)**")
                st.markdown("""
                ✅ **Planning Complet** (.ics)
                ✅ **Analyse Profonde** (Ton mode d'emploi)
                ✅ **Les Prompts Secrets** utilisés :
                """)
                # Affichage style "Code" pour les prompts
                st.markdown('`<System> Act as Neuro-Expert...`')
                st.markdown('`<Strategy> Time-Boxing +20% buffer...`')
                
                st.markdown("<br>", unsafe_allow_html=True)
                # LIEN STRIPE LIVE ICI
                st.link_button("🔓 DÉBLOQUER MAINTENANT", "https://buy.stripe.com/00w7sN5ZW5gp9GggtP0RG00", type="primary")
            
            st.markdown('</div>', unsafe_allow_html=True)