import streamlit as st
import json
import pandas as pd
import plotly.express as px
from backend import parse_schedule, generate_ics_file

st.set_page_config(page_title="Chaos Manager Pro", page_icon="🧠", layout="wide")

# --- CSS PREMIUM (Look & Feel) ---
st.markdown("""
<style>
    /* Style général */
    .stApp { background-color: #0e1117; }
    
    /* La Carte RPG */
    .rpg-card {
        background: linear-gradient(135deg, #1e2130 0%, #0e1117 100%);
        border: 1px solid #2b3042;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    .archetype-title {
        color: #FF4B4B;
        font-size: 28px;
        font-weight: 800;
        text-transform: uppercase;
        margin-bottom: 5px;
        text-align: center;
        letter-spacing: 1px;
    }
    .rarity-badge {
        background-color: #FF4B4B20;
        color: #FF4B4B;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 15px;
    }
    .stat-row {
        display: flex;
        justify_content: space-between;
        margin-bottom: 10px;
        border-bottom: 1px solid #2b3042;
        padding-bottom: 5px;
    }
    .stat-label { color: #a0a5b8; font-size: 14px; }
    .stat-value { color: #ffffff; font-weight: bold; }
    
    /* Le Teaser Flouté */
    .blur-text { filter: blur(4px); user-select: none; color: #666; opacity: 0.6; }
    .locked-section { border: 1px dashed #444; padding: 20px; border-radius: 10px; background-color: #161924; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR (Le Contexte) ---
with st.sidebar:
    st.header("🧠 Chaos Manager V4")
    st.info("Algorithme calibré sur le modèle **Big Five Productivity**.")
    st.markdown("---")
    st.write("Les données psychométriques permettent de définir votre **Profil Cognitif** exact.")

# --- HEADER ---
st.title("🧠 Chaos Manager : Profiler Edition")
st.markdown("### Ne planifie pas juste ta semaine. Hacke ton cerveau.")

st.write("Remplis ce test psychométrique rapide (30 secondes) pour calibrer l'IA.")

# --- FORMULAIRE PSYCHOMÉTRIQUE (Sliders) ---
with st.form("psycho_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Ton Moteur Interne ⚙️")
        
        energy_level = st.select_slider(
            "Niveau d'Énergie actuel :",
            options=["Épuisement (Burnout)", "Faible", "Moyen", "Élevé", "Mode Dieu (Manie)"],
            value="Moyen"
        )
        
        chronotype = st.select_slider(
            "Ton Pic de Performance :",
            options=["🐦 Matin (5h-11h)", "☀️ Journée (11h-17h)", "🌙 Soir (20h-02h)"],
            value="☀️ Journée (11h-17h)"
        )
        
        discipline_score = st.slider("Capacité à faire ce qui est chiant (Discipline) :", 0, 100, 30)

    with col2:
        st.subheader("2. Ta Gestion du Chaos 🌪️")
        
        focus_type = st.radio(
            "Comment tu travailles ?",
            ["🎯 Sniper (Une tâche à la fois)", "🤹 Jongleur (Multitask)", "🦋 Papillon (Distrait)"],
            horizontal=True
        )
        
        stress_reaction = st.select_slider(
            "Face à une deadline urgente :",
            options=["😱 Panique / Paralysie", "😐 Anxiété gérée", "🔥 Excitation / Boost", "🧊 Sang froid total"],
            value="🔥 Excitation / Boost"
        )

    st.markdown("---")
    st.subheader("3. La Variable Cachée 🗝️")
    secret_fear = st.text_input(
        "Sois honnête : Qu'est-ce qui t'a vraiment empêché de réussir ta semaine dernière ?",
        placeholder="Ex: J'ai scrollé TikTok 4h par jour... / J'ai eu peur de commencer...",
    )
    
    st.subheader("4. La Mission (Tâches) 🎯")
    mission_text = st.text_area(
        "Vide ton cerveau ici (Tâches brutes) :",
        placeholder="Ex: Partiel physique vendredi, MMA mardi 19h, rendre projet Python dimanche...",
        height=150
    )

    submitted = st.form_submit_button("🚀 GÉNÉRER MON PROFIL & PLANNING", type="primary", use_container_width=True)

# --- TRAITEMENT ---
if submitted:
    if not mission_text:
        st.warning("Il me faut au moins une mission pour générer un planning !")
    else:
        with st.spinner("Analyse des biais cognitifs... Calcul des scores Big Five..."):
            try:
                # Packaging des données pour le backend
                inputs = {
                    "energy": energy_level,
                    "chronotype": chronotype,
                    "discipline": discipline_score,
                    "focus": focus_type,
                    "stress": stress_reaction,
                    "fear": secret_fear,
                    "mission": mission_text
                }
                
                # APPEL BACKEND
                raw_resp = parse_schedule(inputs)
                data = json.loads(raw_resp)
                
                # Gestion d'erreur
                if "error" in data:
                    st.error(f"🚨 ERREUR : {data['error']}")
                    st.stop()
                
                # --- AFFICHAGE RESULTATS ---
                
                # 1. LA CARTE RPG (Profil)
                st.markdown("---")
                col_card, col_radar = st.columns([1, 1])
                
                with col_card:
                    # Extraction des données pour l'affichage
                    archetype = data.get('archetype', 'Inconnu')
                    rarity = data.get('rarity', 'Top 50%')
                    superpower = data.get('superpower', 'Inconnu')
                    kryptonite = data.get('kryptonite', 'Inconnu')
                    
                    st.markdown(f"""
                    <div class="rpg-card">
                        <div style="text-align:center;"><span class="rarity-badge">✨ Rareté : {rarity}</span></div>
                        <div class="archetype-title">{archetype}</div>
                        <br>
                        <div class="stat-row">
                            <span class="stat-label">⚔️ Super-Pouvoir</span>
                            <span class="stat-value">{superpower}</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">💀 Kryptonite</span>
                            <span class="stat-value">{kryptonite}</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">⚡ Moteur</span>
                            <span class="stat-value">{chronotype}</span>
                        </div>
                        <br>
                        <p style="color:#ccc; font-style:italic; font-size:14px; text-align:center;">
                            "{data.get('quote', 'Pas de citation')}"
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                with col_radar:
                    # Le Radar Plotly
                    st.caption("📊 Empreinte Psychométrique")
                    scores = data.get("scores", {"Focus": 50, "Structure": 50})
                    df_scores = pd.DataFrame(dict(
                        r=list(scores.values()),
                        theta=list(scores.keys())
                    ))
                    fig = px.line_polar(df_scores, r='r', theta='theta', line_close=True, range_r=[0,100])
                    fig.update_traces(fill='toself', line_color='#FF4B4B')
                    fig.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)", 
                        plot_bgcolor="rgba(0,0,0,0)",
                        margin=dict(l=20, r=20, t=20, b=20),
                        polar=dict(
                            radialaxis=dict(visible=True, range=[0, 100], color="#666"),
                            bgcolor="rgba(0,0,0,0)"
                        ),
                        font=dict(color="white")
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # 2. LE PLANNING
                st.subheader("📅 Ton Planning de Combat")
                planning = data.get("planning", [])
                if planning:
                    df = pd.DataFrame(planning)
                    st.dataframe(
                        df[["titre", "start_iso", "end_iso", "categorie"]], 
                        hide_index=True, 
                        use_container_width=True
                    )

                # 3. LE PÉAGE (Expertise)
                st.markdown("---")
                col_lock, col_buy = st.columns([2, 1])
                
                with col_lock:
                    st.markdown('<div class="locked-section">', unsafe_allow_html=True)
                    st.warning("🔒 **ANALYSE STRATÉGIQUE COMPLÈTE**")
                    st.markdown(f"**Pourquoi tu échoues souvent à cause de : '{secret_fear}' ?**")
                    
                    st.write("L'IA a généré ta stratégie corrective :")
                    st.markdown('<p class="blur-text">Ton profil montre un écart critique entre ta Discipline (30) et ton ambition. La méthode Pomodoro classique ne marchera pas sur toi. Il faut utiliser la technique des "Sprints Dopaminergiques" de 25min...</p>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                with col_buy:
                    st.info("📦 **PACK PROFILER**")
                    st.markdown("""
                    - 🧠 **Manuel de ton Cerveau**
                    - 🧬 **Analyse Big Five détaillée**
                    - 📥 **Export Agenda (.ics)**
                    """)
                    
                    # REMETS TON LIEN LIVE ICI
                    st.link_button(
                        "🔓 DÉBLOQUER (9.90€)", 
                        "https://buy.stripe.com/00w7sN5ZW5gp9GggtP0RG00"
                    )

            except Exception as e:
                st.error(f"Erreur système : {e}")