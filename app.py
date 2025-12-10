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

# ... LE RESTE DU CODE (FORMULAIRE) ...
# --- FORMULAIRE ---
st.markdown("#### 1. Calibration Neuro-Psychologique")

st.caption("Importez vos données ou faites une estimation rapide. L'IA va sélectionner les 'Secret Prompts' adaptés à tes scores.")

# ... (Le début du code reste inchangé) ...

with st.form("psycho_form"):
    
    # === C'EST ICI QUE SE TROUVENT LES ONGLETS (TABS) ===
    tab1, tab2 = st.tabs(["📂 J'ai déjà mes scores (Expert)", "🔍 Je ne sais pas (Estimation)"])
 
# --- ONGLET 1 : SAISIE EXPERTE (Sliders + Double Explication) ---
    with tab1:
        st.markdown("""
        <div style="background-color: #1c202a; padding: 15px; border-radius: 8px; margin-bottom: 25px; border: 1px solid #00ff00;">
            ✅ <b>Mode Expert :</b> Ajustez les curseurs selon vos résultats.
            L'IA détecte votre polarité dominante pour calibrer les instructions cachées.
        </div>
        """, unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("##### 🧠 Le Cerveau (Traitement de l'Info)")
            
            # OUVERTURE
            o_score = st.slider("🌊 Ouverture (O) - Créativité", 0, 100, 50, key="o_in")
            st.markdown("""
            <div style="font-size:13px; color:#aaa; margin-bottom:20px; border-left:2px solid #555; padding-left:10px; line-height:1.5;">
                <b>L'impact Productif :</b><br>
                ⬆️ <b>Haut (>75) :</b> Vous êtes un <i>Explorateur</i>. Travailler 4h sur le même sujet vous éteint. L'IA doit alterner les contextes.<br>
                ⬇️ <b>Bas (<25) :</b> Vous êtes un <i>Pragmatique</i>. Vous excellez dans l'approfondissement d'une méthode. L'IA favorisera la répétition efficace.
            </div>
            """, unsafe_allow_html=True)
            
            # CONSCIENCE
            c_score = st.slider("📐 Conscience (C) - Organisation", 0, 100, 50, key="c_in")
            st.markdown("""
            <div style="font-size:13px; color:#aaa; margin-bottom:20px; border-left:2px solid #555; padding-left:10px; line-height:1.5;">
                <b>L'impact Productif :</b><br>
                ⬆️ <b>Haut (>75) :</b> Vous êtes un <i>Architecte</i>. Vous avez besoin d'un plan béton à l'avance pour être serein.<br>
                ⬇️ <b>Bas (<25) :</b> Vous êtes un <i>Pompier</i>. La planification lointaine vous ennuie. L'IA utilisera des "Micro-Deadlines" pour créer l'urgence nécessaire.
            </div>
            """, unsafe_allow_html=True)

            # EXTRAVERSION
            e_score = st.slider("⚡ Extraversion (E) - Énergie Sociale", 0, 100, 50, key="e_in")
            st.markdown("""
            <div style="font-size:13px; color:#aaa; margin-bottom:20px; border-left:2px solid #555; padding-left:10px; line-height:1.5;">
                <b>L'impact Productif :</b><br>
                ⬆️ <b>Haut (>75) :</b> Vous êtes un <i>Connecteur</i>. L'isolement vous vide. L'IA placera les tâches collaboratives aux moments de creux.<br>
                ⬇️ <b>Bas (<25) :</b> Vous êtes un <i>Deep Worker</i>. Les autres drainent votre batterie. L'IA créera des "Sanctuaires de Silence" inviolables.
            </div>
            """, unsafe_allow_html=True)
        
        with col_b:
            st.markdown("##### ❤️ Le Coeur (Gestion Émotionnelle)")
            
            # AGRÉABILITÉ
            a_score = st.slider("🤝 Agréabilité (A) - Coopération", 0, 100, 50, key="a_in")
            st.markdown("""
            <div style="font-size:13px; color:#aaa; margin-bottom:20px; border-left:2px solid #555; padding-left:10px; line-height:1.5;">
                <b>L'impact Productif :</b><br>
                ⬆️ <b>Haut (>75) :</b> Vous êtes un <i>Diplomate</i>. Vous avez du mal à dire non. L'IA bloquera votre temps pour vous protéger.<br>
                ⬇️ <b>Bas (<25) :</b> Vous êtes un <i>Stratège</i>. Vous priorisez la mission sur l'humain. L'IA ira droit au but sans fioritures.
            </div>
            """, unsafe_allow_html=True)
            
            # NÉVROSISME
            n_score = st.slider("🌪️ Névrosisme (N) - Sensibilité Stress", 0, 100, 50, key="n_in")
            st.markdown("""
            <div style="font-size:13px; color:#aaa; margin-bottom:20px; border-left:2px solid #555; padding-left:10px; line-height:1.5;">
                <b>L'impact Productif :</b><br>
                ⬆️ <b>Haut (>75) :</b> Vous êtes une <i>Sentinelle</i>. L'incertitude vous paralyse. L'IA hyper-détaillera le plan pour rassurer votre cerveau.<br>
                ⬇️ <b>Bas (<25) :</b> Vous êtes un <i>Stoïque</i>. Le chaos ne vous touche pas. L'IA vous donnera des objectifs larges et ambitieux.
            </div>
            """, unsafe_allow_html=True)
    # --- ONGLET 2 : SLIDERS (Corrigé & Détaillé) ---
    with tab2:
        st.markdown("""
        <div style="background-color: #262730; padding: 15px; border-radius: 8px; margin-bottom: 20px; font-size: 14px; border: 1px solid #444;">
            ℹ️ <b>Calibration Cognitive :</b> Positionnez le curseur selon votre tendance naturelle. 
            Il n'y a pas de "bon" score. Un score bas en Conscience favorise la créativité, un score haut favorise l'exécution.
        </div>
        """, unsafe_allow_html=True)

        # On utilise des triples guillemets (""") pour éviter le bug des guillemets internes
        
        # --- O : OUVERTURE ---
        st.markdown("#### 🌊 1. Facteur O : La Nouveauté")
        st.caption("🧠 *Impact Travail : Tolérance à la routine vs Besoin d'innovation.*")
        st.markdown("""**0% (Pragmatique)** : J'aime les processus clairs et l'efficacité prouvée.<br>**100% (Explorateur)** : Je m'ennuie vite, j'ai besoin de changer de méthode souvent.""", unsafe_allow_html=True)
        o_est = st.slider("Position O :", 0, 100, 50, key="slider_o", label_visibility="collapsed")
        st.markdown("---")

        # --- C : CONSCIENCE ---
        st.markdown("#### 📐 2. Facteur C : La Structure")
        st.caption("🧠 *Impact Travail : Gestion des délais et finition.*")
        # CORRECTION BUG ICI : On utilise les triples guillemets pour encadrer le tout
        st.markdown("""**0% (Spontané)** : Je travaille par "bursts" d'énergie, flexible mais parfois désordonné.<br>**100% (Architecte)** : Je planifie tout, je suis mal à l'aise sans plan précis.""", unsafe_allow_html=True)
        c_est = st.slider("Position C :", 0, 100, 50, key="slider_c", label_visibility="collapsed")
        st.markdown("---")

        # --- E : EXTRAVERSION ---
        st.markdown("#### ⚡ 3. Facteur E : La Stimulation")
        st.caption("🧠 *Impact Travail : Besoin d'interaction pour réfléchir.*")
        st.markdown("""**0% (Deep Worker)** : L'isolement me rend productif. Le bruit me draine.<br>**100% (Connecteur)** : Je pense en parlant. J'ai besoin du buzz de l'équipe.""", unsafe_allow_html=True)
        e_est = st.slider("Position E :", 0, 100, 50, key="slider_e", label_visibility="collapsed")
        st.markdown("---")

        # --- A : AGRÉABILITÉ ---
        st.markdown("#### 🤝 4. Facteur A : La Coopération")
        st.caption("🧠 *Impact Travail : Capacité à dire Non et négocier.*")
        st.markdown("""**0% (Challenger)** : Je priorise l'objectif, je sais dire non fermement.<br>**100% (Diplomate)** : Je cherche l'harmonie, j'ai du mal à refuser une aide.""", unsafe_allow_html=True)
        a_est = st.slider("Position A :", 0, 100, 50, key="slider_a", label_visibility="collapsed")
        st.markdown("---")

        # --- N : NÉVROSISME ---
        st.markdown("#### 🌪️ 5. Facteur N : La Réactivité")
        st.caption("🧠 *Impact Travail : Gestion du stress et des risques.*")
        st.markdown("""**0% (Roc)** : Le stress glisse sur moi. Calme olympien en crise.<br>**100% (Sentinelle)** : Je repère tous les risques. Le stress peut me paralyser.""", unsafe_allow_html=True)
        n_est = st.slider("Position N :", 0, 100, 50, key="slider_n", label_visibility="collapsed")


    # ... (Le reste du code reste identique) ...
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