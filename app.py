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
    
    /* Le Badge Tech */
    .tech-badge {
        background-color: #1c202a; 
        border: 1px solid #00ff00; 
        color: #00ff00; 
        padding: 4px 8px; 
        border-radius: 4px; 
        font-family: monospace; 
        font-size: 11px;
        display: inline-block;
        margin-bottom: 10px;
        box-shadow: 0 0 8px rgba(0, 255, 0, 0.1);
    }

    /* Boite Explication Scientifique */
    .concept-box {
        background-color: #13151b;
        border-left: 3px solid #FF4B4B;
        padding: 25px;
        border-radius: 0 10px 10px 0;
        margin-bottom: 30px;
        font-size: 15px;
        line-height: 1.6;
    }
    .science-term { color: #FF4B4B; font-weight: bold; }
    
    /* Comparaison Profils (Plus compacte) */
    .profile-example {
        background-color: #21232b;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #333;
        font-size: 13px; /* Police réduite */
    }
    .versus { font-size: 18px; font-weight: bold; color: #666; text-align: center; margin-top: 40px;}
    
    /* Reste du style */
    .rpg-card { background: linear-gradient(135deg, #2b3042 0%, #161924 100%); border: 1px solid #444; border-radius: 15px; padding: 20px; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.4); }
    .archetype-title { color: #FF4B4B; font-size: 26px; font-weight: 800; text-transform: uppercase; margin-top: 10px;}
    .blur-text { filter: blur(5px); user-select: none; color: #888; opacity: 0.7; }
    .locked-section { border: 1px dashed #FF4B4B; padding: 20px; border-radius: 10px; background-color: #1e1111; text-align: center; margin-top: 20px;}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("🧠 Chaos Manager")
    st.caption("v5.1 (Stable)")
    st.markdown('<div class="tech-badge">⚡ CORE: GEMINI 3.0 PRO</div>', unsafe_allow_html=True)
    st.markdown('<div class="tech-badge">🔐 PROMPTS: PROPRIETARY</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.info("💡 **Science du Prompting**\nChaque planning est généré par une injection de prompt unique, calculée selon vos vecteurs de personnalité OCEAN.")

# --- HEADER & PÉDAGOGIE ---
st.title("🧠 Chaos Manager : Expert Edition")
st.markdown("### L'ingénierie IA au service de ton neuro-type.")

# --- L'ARGUMENTAIRE SCIENTIFIQUE (Visible & Direct) ---
st.markdown("""
<div class="concept-box">
    <b>Pourquoi les agendas classiques échouent pour 48% des gens ?</b><br><br>
    Parce qu'ils imposent une structure unique à des cerveaux différents. 
    Notre algorithme repose sur une approche scientifique double :
    <br><br>
    1. 🧬 <b>Le Modèle Big Five (OCEAN) :</b> Nous ne devinons pas qui vous êtes. Nous calibrons l'IA sur vos 5 traits de personnalité fondamentaux (Ouverture, Conscience, Extraversion, Agréabilité, Névrosisme).
    <br><br>
    2. 🤖 <b>Le "Psychometric Prompt Engineering" :</b> C'est notre innovation majeure. Contrairement à ChatGPT qui utilise un ton générique, notre système sélectionne dynamiquement des <i>System Instructions</i> secrètes. 
    <br>
    <i>Exemple : Si vous êtes détecté "Faible Discipline / Haute Impulsion", l'IA n'essaiera pas de vous faire lever à 5h du matin. Elle activera le protocole "Dopamine Sprint" pour maximiser votre hyperfocus.</i>
</div>
""", unsafe_allow_html=True)

st.write("👀 **Visualisez l'impact du Prompting Adaptatif sur 2 profils opposés :**")

# COLONNES COMPACTES
c1, c2, c3 = st.columns([1, 0.15, 1])

with c1:
    st.markdown("""
    <div class="profile-example">
        <strong style="font-size:16px;">👤 Profil A : "Le Soldat"</strong><br>
        <span style="color:#aaa;">(Haute Discipline, Basse Ouverture)</span>
        <hr style="margin:10px 0; border-color:#444;">
        <p style="color:#aaffaa; font-weight:bold;">✅ Stratégie IA générée :</p>
        <ul style="text-align:left; padding-left:20px; margin-bottom:5px;">
            <li>Planning linéaire (9h-18h)</li>
            <li>Pauses fixes de 15 min</li>
            <li>Objectif : Constance</li>
        </ul>
        <i style="color:#666;">-> L'IA agit comme un "Architecte".</i>
    </div>
    """, unsafe_allow_html=True)
    
with c2:
    st.markdown('<div class="versus">VS</div>', unsafe_allow_html=True)
    
with c3:
    st.markdown("""
    <div class="profile-example">
        <strong style="font-size:16px;">👤 Profil B : "L'Artiste"</strong><br>
        <span style="color:#aaa;">(Haute Impulsion, Basse Discipline)</span>
        <hr style="margin:10px 0; border-color:#444;">
        <p style="color:#ffaaaa; font-weight:bold;">✅ Stratégie IA générée :</p>
        <ul style="text-align:left; padding-left:20px; margin-bottom:5px;">
            <li>Blocs "Deep Work" de 4h</li>
            <li>Zéro contrainte le matin</li>
            <li>Objectif : Intensité</li>
        </ul>
        <i style="color:#666;">-> L'IA agit comme un "Coach de Sprint".</i>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("#### 1. Calibration Neuro-Psychologique")
st.caption("Remplis ces jauges. L'IA va sélectionner les 'Secret Prompts' adaptés à tes scores.")

# ... LE RESTE DU CODE (FORMULAIRE) ...
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