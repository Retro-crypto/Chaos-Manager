import streamlit as st
import json
import pandas as pd
import plotly.express as px
from backend import parse_schedule, generate_ics_file

st.set_page_config(page_title="Chaos Manager V6", page_icon="🧠", layout="wide")

# --- CSS & STYLE ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    
    /* Le Badge Tech */
    .tech-badge { background-color: #1c202a; border: 1px solid #00ff00; color: #00ff00; padding: 4px 8px; border-radius: 4px; font-family: monospace; font-size: 11px; display: inline-block; margin-bottom: 10px; box-shadow: 0 0 8px rgba(0, 255, 0, 0.1); }

    /* Boite Explication */
    .concept-box { background-color: #13151b; border-left: 3px solid #FF4B4B; padding: 25px; border-radius: 0 10px 10px 0; margin-bottom: 30px; font-size: 15px; line-height: 1.6; }
    
    /* Comparaison Profils */
    .profile-example { background-color: #21232b; padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #333; font-size: 13px; }
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
    st.caption("v6.0 (Neuro-Engine)")
    st.markdown('<div class="tech-badge">⚡ CORE: GEMINI 3.0 PRO</div>', unsafe_allow_html=True)
    st.markdown('<div class="tech-badge">🧬 INPUT: MULTI-VECTOR</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.info("💡 **Science**\nNous croisons votre profil **OCEAN** (Cerveau Inné) avec vos **Métriques de Travail** (Habitudes Acquises) pour générer le prompt parfait.")

# --- HEADER ---
st.title("🧠 Chaos Manager : Expert Edition")
st.markdown("### L'ingénierie IA au service de ton neuro-type.")

# --- PÉDAGOGIE ---
st.markdown("""
<div class="concept-box">
    <b>Pourquoi connaître son type OCEAN ne suffit pas ?</b><br><br>
    Savoir que vous êtes "Consciencieux" (Test OCEAN/MBTI) est un bon début. Mais cela ne dit pas comment vous réagissez à une deadline de 2h ou au bruit ambiant.<br>
    Notre algorithme <b>Neuro-Cross™</b> croise deux couches de données :
    <br>
    1. 🧠 <b>Le Hardware (Votre Personnalité) :</b> Vos traits innés (OCEAN).
    <br>
    2. ⚙️ <b>Le Software (Votre Modus Operandi) :</b> Vos mécanismes de travail actuels (Focus, Résistance au stress, Chronotype).
</div>
""", unsafe_allow_html=True)

# --- FORMULAIRE ---
st.write("#### 1. Calibration du 'Hardware' (Personnalité)")
st.caption("Importez vos données ou faites une estimation rapide.")

with st.form("psycho_form"):
    
    # === C'EST ICI QUE SE TROUVENT LES ONGLETS (TABS) ===
    tab1, tab2 = st.tabs(["📂 J'ai déjà mes scores OCEAN", "🔍 Je ne sais pas (Estimation)"])
    
    # Onglet 1 : Saisie Manuelle (Pour les experts)
    with tab1:
        st.info("Entrez les pourcentages obtenus sur BigFive-Test ou convertissez vos lettres MBTI.")
        c1, c2, c3, c4, c5 = st.columns(5)
        # On met 0 par défaut pour savoir si l'utilisateur a rempli ou pas
        o_score = c1.number_input("Ouverture", 0, 100, 0, key="o_in")
        c_score = c2.number_input("Conscience", 0, 100, 0, key="c_in")
        e_score = c3.number_input("Extraversion", 0, 100, 0, key="e_in")
        a_score = c4.number_input("Agréabilité", 0, 100, 0, key="a_in")
        n_score = c5.number_input("Névrosisme", 0, 100, 0, key="n_in")

    # Onglet 2 : Sliders (Pour les autres)
    with tab2:
        st.write("Estimez-vous honnêtement sur ces échelles :")
        col_est1, col_est2 = st.columns(2)
        with col_est1:
            o_est = st.slider("Ouverture (Besoin de nouveauté / Curiosité)", 0, 100, 50)
            c_est = st.slider("Conscience (Discipline / Organisation)", 0, 100, 50)
            e_est = st.slider("Extraversion (Besoin social / Énergie externe)", 0, 100, 50)
        with col_est2:
            a_est = st.slider("Agréabilité (Empathie / Tendance à dire oui)", 0, 100, 50)
            n_est = st.slider("Névrosisme (Sensibilité au stress / Anxiété)", 0, 100, 50)

    st.markdown("---")
    st.write("#### 2. Calibration du 'Software' (Méthodes de Travail)")
    st.caption("Comment votre cerveau fonctionne-t-il *en situation* ?")
    
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        focus_span = st.select_slider(
            "⏱️ Endurance de Concentration Max :",
            options=["15 min (TDAH)", "45 min (Standard)", "2h (Deep Work)", "4h+ (Hyperfocus)"]
        )
        deadline_react = st.radio(
            "💣 Face à une urgence :",
            ["Je paralyse", "Je procrastine jusqu'à la fin", "Je m'active (Adrénaline)", "Je planifie froidement"]
        )
    
    with col_w2:
        chronotype = st.selectbox(
            "⏰ Votre Pic Biologique :",
            ["Matin (06h-11h)", "Après-midi (14h-18h)", "Soirée (21h-00h)", "Nuit Profonde (00h-04h)"]
        )
        environment = st.selectbox(
            "🔊 Environnement requis :",
            ["Silence absolu", "Bruit blanc / LoFi", "Chaos ambiant / Café", "Musique agressive"]
        )

    st.markdown("---")
    st.write("#### 3. La Mission")
    mission = st.text_area("Vos impératifs (Vrac accepté) :", placeholder="Ex: Rendre projet Python, Sport ce soir...", height=100)
    
    submitted = st.form_submit_button("🚀 LANCER L'ANALYSE NEURO-CROSS", type="primary", use_container_width=True)

# --- LOGIQUE ---
if submitted:
    # Logique intelligente : Si l'utilisateur a rempli l'onglet 1 (scores > 0), on prend ça. Sinon on prend les sliders.
    if o_score + c_score + e_score > 0:
        # L'utilisateur a utilisé l'onglet 1
        final_scores = {"Ouverture": o_score, "Conscience": c_score, "Extraversion": e_score, "Agréabilité": a_score, "Névrosisme": n_score}
    else:
        # L'utilisateur a utilisé l'onglet 2 (ou rien touché)
        final_scores = {"Ouverture": o_est, "Conscience": c_est, "Extraversion": e_est, "Agréabilité": a_est, "Névrosisme": n_est}

    if not mission:
        st.warning("Donne-moi au moins une tâche !")
    else:
        with st.spinner("Croisement des vecteurs OCEAN & Habitudes..."):
            
            # Inputs complets pour le backend
            inputs = {
                "scores": final_scores,
                "work_style": {
                    "focus": focus_span,
                    "deadline": deadline_react,
                    "chrono": chronotype,
                    "env": environment
                },
                "mission": mission
            }
            
            # Appel Backend
            data = json.loads(parse_schedule(inputs))
            
            # --- RÉSULTATS (Carte & Radar) ---
            st.markdown("---")
            col_card, col_radar = st.columns([1, 1])
            
            with col_card:
                st.markdown(f"""
                <div class="rpg-card">
                    <div style="font-size:12px; color:#FF4B4B; font-weight:bold;">🧬 PROFIL NEURO-CROSS : {data.get('rarity')}</div>
                    <div class="archetype-title">{data.get('archetype')}</div>
                    <p style="font-style:italic; color:#aaa; margin-top:10px;">"{data.get('quote')}"</p>
                    <hr style="border-color:#444;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                        <span>⚔️ Levier Principal :</span><span style="color:white; font-weight:bold;">{data.get('superpower')}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between;">
                        <span>⚠️ Point de Rupture :</span><span style="color:white; font-weight:bold;">{data.get('kryptonite')}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            with col_radar:
                # Radar (Basé sur les scores OCEAN)
                df_scores = pd.DataFrame(dict(r=list(final_scores.values()), theta=list(final_scores.keys())))
                fig = px.line_polar(df_scores, r='r', theta='theta', line_close=True, range_r=[0,100])
                fig.update_traces(fill='toself', line_color='#FF4B4B')
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
                st.plotly_chart(fig, use_container_width=True)

            # --- TEASING PLANNING ---
            st.markdown("---")
            st.subheader("📅 Votre Stratégie Temporelle (Aperçu)")
            
            planning = data.get("planning", [])
            if len(planning) > 0:
                df_free = pd.DataFrame(planning[:2])
                st.dataframe(df_free[["titre", "start_iso", "end_iso", "categorie"]], hide_index=True, use_container_width=True)
            
            # --- PAYWALL ---
            st.markdown('<div class="locked-section">', unsafe_allow_html=True)
            st.write("🔒 **RAPPORT NEURO-PSYCHOLOGIQUE COMPLET VERROUILLÉ**")
            
            col_blur, col_pitch = st.columns([1.5, 1])
            with col_blur:
                st.markdown("#### Analyse Croisée (OCEAN x Habitudes) :")
                st.markdown(f'<div class="blur-text">Votre Conscience ({final_scores["Conscience"]}%) entre en conflit avec votre habitude "{deadline_react}". L IA a détecté un risque élevé de paralysie décisionnelle à 14h...</div>', unsafe_allow_html=True)
                st.markdown("#### Les Prompts Secrets Activés :")
                st.markdown('<div class="blur-text"><System> Override circadian rythm for Night Owl profile...</div>', unsafe_allow_html=True)

            with col_pitch:
                st.info("📦 **PACK EXPERT (9.90€)**")
                st.markdown("""
                ✅ **Planning Intégral** (.ics)
                ✅ **Analyse Neuro-Cross** (Pourquoi vous bloquez)
                ✅ **Les Prompts Secrets** (Recette)
                """)
                # LIEN STRIPE LIVE ICI (Celui que tu m'as donné)
                st.link_button("🔓 DÉBLOQUER MAINTENANT", "https://buy.stripe.com/00w7sN5ZW5gp9GggtP0RG00", type="primary")
            
            st.markdown('</div>', unsafe_allow_html=True)