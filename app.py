import streamlit as st
import json
import pandas as pd
import textwrap
import time
import random
import plotly.express as px
import plotly.graph_objects as go # Pour les graphiques avancés
from backend import parse_schedule, generate_ics_file, save_lead_to_gsheet
STRIPE_LINK = "https://buy.stripe.com/00w7sN5ZW5gp9GggtP0RG00"

# --- INITIALISATION DE LA MÉMOIRE (OBLIGATOIRE) ---
if 'data' not in st.session_state:
    st.session_state['data'] = {} # On crée un dictionnaire vide par défaut


st.set_page_config(page_title="Chaos Manager V5", page_icon="🧠", layout="wide")

# --- CSS & STYLE (THEME CLAIR "ZEN ARCHITECT") ---
st.markdown("""
<style>
    /* --- GENERAL SETTINGS --- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    .stApp { 
        background-color: #f8f9fa; /* Gris très pâle (Papier) */
        font-family: 'Inter', sans-serif;
        color: #1a1a1a;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #111;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    p, div, span {
        color: #444; /* Gris lecture */
    }

    /* --- LE BOUTON D'ACTION (Style Stripe/Airbnb) --- */
    .stButton > button {
        background-color: #111; /* Noir Profond */
        color: white;
        border: none;
        padding: 16px 32px;
        font-size: 16px;
        font-weight: 600;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.2s ease;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.15);
        background-color: #333;
    }
    .stButton > button:active {
        transform: scale(0.98);
    }

    /* --- RADIO BUTTONS : GRID CARDS (CLEAN) --- */
    div[role="radiogroup"] {
        display: grid !important;
        grid-template-columns: 1fr !important;
        gap: 12px !important;
        width: 100% !important;
    }

    /* Les Cartes (Tuiles) */
    div[role="radiogroup"] > label {
        background-color: #ffffff !important;
        border: 1px solid #e0e0e0 !important;
        padding: 20px !important;
        border-radius: 10px !important;
        margin: 0 !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
        
        width: 100% !important; 
        height: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
    }
    
    /* Effet Survol */
    div[role="radiogroup"] > label:hover {
        border-color: #111 !important;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.05) !important;
    }

    /* Sélection */
    div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #111 !important; /* Carte devient noire */
        border-color: #111 !important;
        color: white !important;
    }
    
    /* Inversion des couleurs du texte quand sélectionné */
    div[role="radiogroup"] > label[data-checked="true"] p {
        color: white !important;
    }
    div[role="radiogroup"] > label[data-checked="true"] span {
        color: #ccc !important;
    }

    /* Typographie des cartes */
    div[role="radiogroup"] label p {
        font-weight: 700 !important;
        font-size: 15px !important;
        color: #111 !important;
        margin-bottom: 4px !important;
    }
    div[role="radiogroup"] label span {
        font-size: 13px !important;
        color: #666 !important;
        line-height: 1.4 !important;
    }

    /* --- INPUTS & TEXTAREAS --- */
    .stTextArea textarea, .stTextInput input {
        background-color: #ffffff !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 8px !important;
        color: #111 !important;
        box-shadow: inset 0 1px 2px rgba(0,0,0,0.02) !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #111 !important;
        box-shadow: 0 0 0 2px rgba(0,0,0,0.1) !important;
    }
    .stTextArea label {
        color: #111 !important;
        font-weight: 600 !important;
    }

    /* --- BOITES D'INFORMATION (ALERTS) --- */
    .stAlert {
        background-color: #fff !important;
        border: 1px solid #eee !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03) !important;
        color: #444 !important;
    }
    
    /* --- CUSTOM CONTAINERS --- */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff !important;
        border: 1px solid #e5e5e5 !important;
        border-radius: 12px !important;
        padding: 24px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02) !important;
    }
    
    /* --- ELEMENTS SPECIFIQUES --- */
    .concept-box { 
        background-color: #fff; 
        border-left: 4px solid #111; 
        padding: 24px; 
        border-radius: 0 8px 8px 0; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.03); 
        margin-bottom: 30px; 
        border: 1px solid #f0f0f0;
    }
    
    .profile-example { 
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 12px; 
        text-align: center; 
        border: 1px solid #eaeaea; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }
    
    .tech-badge { 
        background-color: #f0f2f6; 
        border: 1px solid #d1d5db; 
        color: #4b5563; 
        padding: 4px 10px; 
        border-radius: 4px; 
        font-family: monospace; 
        font-size: 11px; 
        font-weight: bold; 
    }
    
    .rpg-card { 
        background: #ffffff; 
        border: 1px solid #eee; 
        border-radius: 16px; 
        padding: 25px; 
        text-align: center; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.05); 
    }
    
    .archetype-title { 
        color: #111; 
        font-size: 28px; 
        font-weight: 900; 
        text-transform: uppercase; 
        margin-top: 10px; 
        letter-spacing: -1px;
    }
/* --- MODIFICATION UNIQUEMENT BARRE GAUCHE & HAUT --- */

    /* 1. La Barre Latérale (Sidebar) en BEIGE */
    section[data-testid="stSidebar"] {
        background-color: #F5F1E6 !important; /* Beige "Parchemin" doux */
        border-right: 1px solid #E6E2D3 !important; /* Bordure discrète */
    }
    
    /* On s'assure que le texte dans le beige reste bien lisible (Gris foncé) */
    section[data-testid="stSidebar"] * {
        color: #2c2c2c !important;
    }

    /* 2. La Barre du Haut (Header) pour virer le noir/blanc moche */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }
    /* --- TABS --- */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: transparent; 
        border-radius: 4px; 
        color: #666; 
        font-weight: 500;
        border: none;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #fff !important; 
        color: #111 !important; 
        font-weight: bold;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-bottom: 2px solid #111;
    }
    
    /* --- Paywall Teaser Light --- */
    .teaser-box {
        background-color: white;
        border: 1px solid #eee;
        border-radius: 12px;
        padding: 25px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.04);
    }

    hr { border-color: #eee !important; }
/* LIGNE DE SÉPARATION ÉLÉGANTE */
    .section-divider {
        margin-top: 60px;       /* Espace au-dessus */
        margin-bottom: 60px;    /* Espace en-dessous */
        border: 0;
        border-top: 1px solid #d1d5db; /* Trait gris "pro" */
    }
    

    /* Pour éviter que les titres dans les cadres ne collent trop au bord haut */
    .section-frame > h1:first-child, 
    .section-frame > h2:first-child, 
    .section-frame > h3:first-child, 
    .section-frame > h4:first-child,
    .section-frame > .stMarkdown:first-child h5 {
         margin-top: 0 !important;
    }
    /* --- STYLE STYLE 16PERSONALITIES --- */

    .main-title {
        text-align: center;
        font-size: 3rem !important; /* Très gros */
        font-weight: 800 !important;
        color: #1a1a1a !important;
        margin-bottom: 10px !important;
    }

    /* Le Sous-titre centré */
    .subtitle {
        text-align: center;
        font-size: 1.2rem !important;
        color: #666 !important;
        margin-bottom: 50px !important;
        max-width: 700px;
        margin-left: auto;
        margin-right: auto;
    }

    /* Les Cartes "Étapes" */
    .step-card {
        background-color: #FFFFFF;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 30px 20px;
        text-align: center;
        height: 100%; /* Pour qu'elles aient la même hauteur */
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .step-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(46, 125, 50, 0.15); /* Ombre verte au survol */
        border-color: #2E7D32;
    }

    /* Le Badge "Étape 1" */
    .step-badge {
        background-color: #E8F5E9; /* Vert très clair */
        color: #2E7D32; /* Vert sapin */
        font-weight: 700;
        font-size: 0.8rem;
        padding: 5px 10px;
        border-radius: 20px;
        display: inline-block;
        margin-bottom: 15px;
    }

    /* L'emoji/Icone */
    .step-icon {
        font-size: 3rem;
        margin-bottom: 15px;
        display: block;
    }

    /* Titre de la carte */
    .step-title {
        font-weight: 700;
        font-size: 1.1rem;
        color: #1a1a1a;
        margin-bottom: 10px;
    }

    /* Texte de la carte */
    .step-desc {
        font-size: 0.9rem;
        color: #666;
        line-height: 1.5;
    }
       
    /* --- STYLE TIMELINE PLANNING --- */
    .timeline-row {
        display: flex;
        margin-bottom: 20px;
        align-items: flex-start;
    }

    .time-col {
        width: 60px;
        font-weight: 700;
        color: #2E7D32; /* Ton Vert */
        font-size: 14px;
        padding-top: 15px; /* Pour aligner avec la carte */
    }

    .card-col {
        flex-grow: 1;
        background: #ffffff;
        border-left: 4px solid #2E7D32; /* La barre de couleur à gauche */
        border-radius: 0 12px 12px 0; /* Arrondi seulement à droite */
        padding: 15px 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        border: 1px solid #f0f0f0;
    }

    .card-title {
        font-weight: 700;
        color: #111;
        font-size: 16px;
        margin-bottom: 5px;
    }

    /* LE FLOU MAGIQUE */
    .blur-content {
        color: #666;
        font-size: 14px;
        filter: blur(5px); /* C'est ça qui cache le secret */
        user-select: none; /* Empêche de sélectionner le texte pour tricher */
        opacity: 0.7;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.hero-card{
  background:#fff;
  border:1px solid #e0e0e0;
  border-radius:16px;
  padding:40px;
  box-shadow:0 4px 20px rgba(0,0,0,0.05);
  margin-bottom:30px;
}
</style>
""", unsafe_allow_html=True)


# 1. TITRE & ACCROCHE


st.markdown("""
<div style="text-align: center; max-width: 850px; margin: 0 auto; margin-bottom: 50px; margin-top: 20px;">

<h1 style="color: #111; font-weight: 900; font-size: 42px; margin: 0; line-height: 1.2;">
Votre cerveau n'est pas buggé.
</h1>
<h2 style="color: #2E7D32; font-weight: 600; font-size: 32px; margin-top: 5px; margin-bottom: 40px;">
Il est juste mal réglé.
</h2>

<div style="text-align: left; background-color: #FFFFFF; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); border: 1px solid #e0e0e0;">

<p style="font-size: 18px; font-weight: 500; color: #444; margin-bottom: 20px; border-left: 4px solid #2E7D32; padding-left: 20px; line-height: 1.5;">
🤯 Avez-vous 10 nouvelles idées par semaine, mais aucune terminée à la fin du mois ?
</p>

<p style="font-size: 18px; font-weight: 500; color: #444; margin-bottom: 20px; border-left: 4px solid #2E7D32; padding-left: 20px; line-height: 1.5;">
⚡ Êtes-vous capable d'apprendre n'importe quoi en 24h, mais paralysé par l'ennui dès que ça devient répétitif ?
</p>

<p style="font-size: 18px; font-weight: 500; color: #444; margin-bottom: 0; border-left: 4px solid #2E7D32; padding-left: 20px; line-height: 1.5;">
🗣️ Vous dit-on souvent <i>"Tu as du potentiel"</i> alors que vous avez l'impression de faire du surplace ?
</p>

</div>

</div>
""", unsafe_allow_html=True)


# 2. LES 3 ÉTAPES (GRID)
col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    st.markdown("""
    <div class="step-card">
        <span class="step-badge">ÉTAPE 1</span>
        <span class="step-icon">🧩</span>
        <div class="step-title">Le Profilage</div>
        <div class="step-desc">
            Répondez à 5 curseurs simples pour définir votre mécanique mentale (OCEAN, Stress, Énergie).
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="step-card">
        <span class="step-badge">ÉTAPE 2</span>
        <span class="step-icon">🧬</span>
        <div class="step-title">L'Analyse IA</div>
        <div class="step-desc">
            Gemini croise vos données avec les neurosciences pour identifier vos leviers de performance.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="step-card">
        <span class="step-badge">ÉTAPE 3</span>
        <span class="step-icon">🚀</span>
        <div class="step-title">Le Protocole</div>
        <div class="step-desc">
            Obtenez votre emploi du temps "anti-procrastination" et vos hacks cognitifs personnalisés.
        </div>
    </div>
    """, unsafe_allow_html=True)

# Espace pour respirer avant le formulaire
st.markdown("<br><br>", unsafe_allow_html=True)


    
# --- FORMULAIRE ---
with st.container(border=False):
    st.markdown("<br>", unsafe_allow_html=True)
    

    with st.form("psycho_form"):
        
        # CRÉATION DES 7 ONGLETS (Nouvelle structure)
        tab_ocean, tab_chrono, tab_archi, tab_genius, tab_invest, tab_mode, tab_input = st.tabs([
            "1. 🧠 Personnalité", 
            "2. 🦁 Chronobiologie", 
            "3. 📐 Architecture", 
            "4. ⚙️ Type d'Effort", 
            "5. 🎯 Vos ambitions",
            "6. 🎯 Votre mode de vie",
            "7. 📝 Le Vortex"       
        ])

        # ==========================================================================
        # ONGLET 1 : MODULE 1 (PROFIL NEURO)
        # ==========================================================================
        with tab_ocean:
            
            
            # LES SLIDERS (INPUTS)
            col_brain, col_heart = st.columns(2, gap="medium")


            with col_brain:
                with st.container(border=True):
                    st.markdown("### **1. Votre rapport au changement ?**")
                    # Plus d'explication texte, juste l'échelle visuelle
                    o_score = st.slider("O", 0, 100, 50, key="slider_o", label_visibility="collapsed")
                    st.markdown('<div style="font-size:12px; color:#555; display:flex; justify-content:space-between;"><span>J\'aime la Routine</span><span>J\'ai besoin de Nouveauté</span></div>', unsafe_allow_html=True)

                with st.container(border=True):
                    st.markdown("### **2. Votre mode d'organisation ?**")
                    c_score = st.slider("C", 0, 100, 50, key="slider_c", label_visibility="collapsed")
                    st.markdown('<div style="font-size:12px; color:#555; display:flex; justify-content:space-between;"><span>Improvisation / Feeling</span><span>Planification / Carré</span></div>', unsafe_allow_html=True)

                with st.container(border=True):
                    st.markdown("### **3. Comment rechargez-vous vos batteries ?**")
                    e_score = st.slider("E", 0, 100, 50, key="slider_e", label_visibility="collapsed")
                    st.markdown('<div style="font-size:12px; color:#555; display:flex; justify-content:space-between;"><span>Seul (Solitude)</span><span>Avec des gens (Groupe)</span></div>', unsafe_allow_html=True)

            with col_heart:
                with st.container(border=True):
                    st.markdown("### **4. Votre attitude face au désaccord ?**")
                    a_score = st.slider("A", 0, 100, 50, key="slider_a", label_visibility="collapsed")
                    st.markdown('<div style="font-size:12px; color:#555; display:flex; justify-content:space-between;"><span>Direct & Franc (Le résultat compte)</span><span>Consensuel (L\'humain compte)</span></div>', unsafe_allow_html=True)

                with st.container(border=True):
                    st.markdown("### **5. Votre gestion du stress ?**")
                    n_score = st.slider("N", 0, 100, 50, key="slider_n", label_visibility="collapsed")
                    st.markdown('<div style="font-size:12px; color:#555; display:flex; justify-content:space-between;"><span>Imperméable / Zen</span><span>Sensible / Inquiet</span></div>', unsafe_allow_html=True)
        # ==========================================================================
        # ONGLET 2 : MODULE 2 (CHRONOTYPE)
        # ==========================================================================
            
        with tab_chrono:
            # DANS L'ONGLET CHRONOBIOLOGIE
            # --- CSS ROBUSTE (CARTES CLIQUABLES) ---
            # --- CSS CORRIGÉ (ALIGNEMENT GAUCHE STRICT) ---
            st.markdown("""
            <style>
            /* 1. La boite globale (La Carte) */
            div[role="radiogroup"] > label {
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
                margin-bottom: 10px;
                width: 100%;
                
                /* C'est ici que ça se joue : Flexbox horizontal aligné à gauche */
                display: flex !important;
                flex-direction: row !important;
                justify-content: flex-start !important; /* FORCE GAUCHE */
                align-items: center !important;         /* Centre verticalement */
                
                cursor: pointer;
                transition: all 0.2s;
            }

            /* 2. Effet au survol */
            div[role="radiogroup"] > label:hover {
                background-color: #ffffff;
                border-color: #111;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            }

            /* 3. Le petit rond (Radio) */
            div[role="radiogroup"] label > div:first-child {
                margin-right: 15px !important; /* Espace entre le rond et le texte */
            }

            /* 4. Le texte */
            div[role="radiogroup"] label > div:last-child {
                text-align: left !important; /* Force le texte à gauche */
                width: 100%;
            }
            </style>
            """, unsafe_allow_html=True)

            # --- LE CONTENU ---
            st.markdown("### ⏰ Quel est votre rythme naturel ?")

            chronotype_input = st.radio(
                "Chronotype",
                [
                    "**Matinal** : Réveil naturel avant l'heure. Productif le matin, fatigué le soir.",
                    "**Intermédiaire** : Besoin de 8h fixes. Performant en horaires de bureau (9h-18h).",
                    "**Tardif** : Brouillard matinal. Le cerveau s'allume tard. Créatif la nuit.",
                    "**Irrégulier** : Sommeil haché. Énergie imprévisible. Souvent fatigué."
                ],
                label_visibility="collapsed"
            )

            # Extraction propre
            chronotype = chronotype_input.split("**")[1].strip()

            
        
            

        # ==========================================================================
        # ONGLET 3 : MODULE 3 (ARCHITECTURE)
        # ==========================================================================
        with tab_archi:
            st.markdown("### Quelle est votre manière de penser ?")
            c_input, c_theory = st.columns([1.5, 1], gap="large")
            with c_input:
                
                arch_type = st.radio(
                    "Architecture", 
                    [
                        "🛠️ **Deep Work (Logique)**\nCode, Rédaction, Analyse. J'ai besoin de silence total et de 0 distraction. Tolérance zéro au bruit.",
                        "⚖️ **Social (Humain)**\nRéunions, Appels, Négociation. Je dois utiliser mon intelligence émotionnelle. Le bruit ne me dérange pas.",
                        "🌀 **Stratégie (Vision)**\nConnecter des idées, brainstormer, planifier. J'ai besoin de recul et de marcher."
                    ], 
                    label_visibility="collapsed"
                )

        # ==========================================================================
        # ONGLET 4 : MODULE 4 (GENIUS)
        # ==========================================================================

        
        with tab_genius:
            st.markdown("### Comment travaillez-vous ?")
            c_input, c_theory = st.columns([1.5, 1], gap="large")
            with c_input:
                
                work_genius = st.radio(
                    "Génie", 
                    [
                        "✨ **Syndrôme de la page Blanche : **\nJ'ai plein d'idées mais j'ai du mal à commencer.",
                        "🔥 **Le Ventre Mou : **\nJe commence souvent fort, mais dès que ça devient ennuyeux, j'ai du mal à persévérer",
                        "🏗️ **La Finition : **\nJe fais souvent le plus gros du travail , mais les derniers détails m'angoissent."
                    ], 
                    label_visibility="collapsed"
                )

        # ==========================================================================
        # ONGLET 5 : MODULE 5 (INVESTISSEMENT)
        # ==========================================================================
        with tab_invest:
            st.markdown("### A quel point comptez-vous travailler pour vos projets ?")
            c_life_input, c_life_theory = st.columns([1.5, 1], gap="large")
            with c_life_input:
                life_phase = st.radio("Phase", [
                "🔥 **Phase de sprint : ** Deadline imminente, surcharge temporaire acceptée",
                "🏗️ **Construction lente : ** Projet de fond, besoin de blocs longs et stables",
                "⚖️ **Rythme tranquille : ** Maintenance, gestion des flux, équilibre",
                "🌱 **Regénération : ** Post-burnout, priorité à la dette de sommeil"
                ])
            
    # ==========================================================================
    # ONGLET 6 : MODULE 6 (MODE DE VIE)
    # ==========================================================================
        with tab_mode:
                
            c_life_input, c_life_theory = st.columns([1.5, 1], gap="large")
            
            with c_life_input:
            
                user_status = st.radio("Situation", [
                "🎓 **Étudiant** (Horaires flous, charge de révision, examens)",
                "💼 **Salarié / Cadre** (Horaires imposés, réunions, hiérarchie)",
                "🚀 **Freelance / Entrepreneur** (Liberté totale, risque de chaos)",
                "🏠 **Parent / Foyer** (Temps fragmenté, charge mentale)"
            ])
    # ==========================================================================
    # ONGLET 7 : LES FACTEURS FREINANTS
    # ==========================================================================
    with tab_input:

        c_frict_input, c_frict_theo = st.columns([2, 1], gap="large")
        
        with c_frict_input:
            # INTERNE
            st.markdown("**👹 Sabotage Interne (Vous)**")
            friction_internal = st.text_area(
                "Interne", 
                placeholder="Ex: Je suis fatigué, j'ai peur de commencer, je m'ennuie...", 
                height=100, 
                label_visibility="collapsed", 
                key="frict_int"
            )
            
            # EXTERNE
            st.markdown("**🔊 Sabotage Externe (Le Monde)**")
            friction_external = st.text_area(
                "Externe", 
                placeholder="Ex: Travaux bruyants, téléphone qui sonne, enfants...", 
                height=100, 
                label_visibility="collapsed", 
                key="frict_ext"
            )
            
        with c_frict_theo:
            with st.expander("🔍 Besoin d'aide pour identifier ?", expanded=True):
                st.markdown("""
                **👹 Pistes Sabotage Interne :**
                * **L'Inertie :** "La tâche semble trop grosse."
                * **Le Perfectionnisme :** "Peur que ce soit nul."
                * **L'Ennui :** "C'est trop répétitif."
                * **La Fatigue :** "Brouillard mental."
                
                **🔊 Pistes Sabotage Externe :**
                * **Le Numérique :** "Notifs Slack/Insta."
                * **L'Humain :** "Collègues qui interrompent."
                * **Le Sonore :** "Bruit ambiant / Travaux."
                * **L'Imprévu :** "Urgences externes."
                """)
            

        st.markdown("---")
        st.markdown("###### Recevez votre analyse par mail.")
        
        # LE CHAMP EMAIL (OBLIGATOIRE)
        user_email = st.text_input(
            "Votre Email", 
            placeholder="exemple@email.com", 
            label_visibility="collapsed"
        )
        
        st.caption("Sans cela, vous ne pourrez recevoir votre protocole par mail.")
        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- LOGIQUE DU BOUTON INTELLIGENT ---
        st.markdown("""
<style>
/* Cible uniquement les boutons "Primary" (ceux en vert) */
div.stButton > button[kind="primary"] {
    color: #FFFFFF !important; /* Force le BLANC */
    font-weight: 700 !important; /* Gras pour que ça ressorte bien */
    border: 1px solid rgba(255,255,255,0.2) !important; /* Petite bordure subtile pour le relief */
}
</style>
""", unsafe_allow_html=True)
        # 1. Logique d'affichage du bouton (Disparaît si analyse faite)
        submitted = st.form_submit_button("🚀 GÉNÉRER MON PROTOCOLE OPTIMISÉ", type="primary", use_container_width=True)

        # 2. Exécution Logique (Si clic)
        if submitted:
            # A. Barrière de sécurité (Email)
            if not user_email or "@" not in user_email:
                st.error("⚠️ L'analyse requiert une adresse email valide pour l'envoi du protocole.")
                st.stop()

            # B. Consolidation des Inputs
            # Valeurs par défaut blindées pour éviter le crash
            current_mission = locals().get('mission', "Restructuration Cognitive")
            time_range = locals().get('time_range', (9, 18))
            current_timerange = f"{time_range[0]}h00 - {time_range[1]}h00"

            # Logique de Tendance (Interne)
            if c_score >= 75: tendency = "ARCHITECTE"
            elif c_score <= 30: tendency = "CHAOS PILOT"
            else: tendency = "HYBRIDE"

            final_scores = {
                "Ouverture": o_score, "Conscience": c_score, 
                "Extraversion": e_score, "Agréabilité": a_score, "Névrosisme": n_score
            }

            inputs = {
                "scores": final_scores,
                "work_style": {
                    "chronotype": chronotype,
                    "architecture": arch_type,
                    "genius": work_genius,
                    "tendency": tendency,
                    "status": user_status
                },
                "context": {
                    "phase_de_vie": life_phase,
                    "mission": current_mission,
                    "horaires": current_timerange,
                    "frictions_internes": friction_internal,
                    "frictions_externes": friction_external
                }
            }

            # --- C. LE THÉÂTRE DU CALCUL (Psychologie de la Valeur) ---
            # On remplace le spinner simple par une progression narrative
            
            progress_bar = st.progress(0, text="Initialisation du Core Gemini...")
            status_text = st.empty() # Placeholder pour le texte qui change
            
            # Séquence de "Scanning" (Purement cosmétique mais vital pour la conversion)
            loading_steps = [
                (10, "🔄 Synchronisation avec l'API Gemini Pro..."),
                (25, "🧠 Analyse de la topographie O.C.E.A.N..."),
                (40, "📉 Détection des fuites de dopamine..."),
                (60, "📐 Calibrage des cycles ultradiens..."),
                (75, "🔨 Architecture de la journée idéale en cours..."),
                (90, "⚡ Optimisation des blocs de Deep Work..."),
                (100, "✅ Génération du Rapport Neuro-Stratégique terminée.")
            ]
            
            # On lance le calcul RÉEL en tâche de fond (ici synchrone mais masqué par l'anim)
            # Pour l'UX, on force un délai minimum pour que l'utilisateur "sente" le calcul
            start_time = time.time()
            
            # Appel Backend (Le vrai calcul)
            raw_result = parse_schedule(inputs)
            
            # On joue l'animation pendant que (ou après que) le calcul se fait
            for percent, label in loading_steps:
                # Petite pause artificielle pour donner du poids (0.3s à 0.6s aléatoire)
                time.sleep(random.uniform(0.3, 0.7)) 
                progress_bar.progress(percent, text=label)
            
            status_text.empty() # Nettoyage
            progress_bar.empty() # Nettoyage

            # --- D. GESTION DES ERREURS & SUCCÈS ---
            
            if not raw_result:
                st.error("❌ Erreur technique : Le 'Cerveau' n'a pas répondu. Regarde le terminal (écran noir) pour voir le détail du bug.")
                st.stop()

            # E. Mapping Critique (Backend -> Frontend Storage)
            formatted_data = {
                "analysis_report": raw_result.get("teaser_html", "<p>Données non structurées.</p>"),
                "typical_day": raw_result.get("preview_day", []),
                "chart_energy": raw_result.get("chart_energy", []),
                "chart_matrix": raw_result.get("chart_matrix", []),
                "chart_fogg": raw_result.get("chart_fogg", []),
                "archetype": raw_result.get("archetype", "Inconnu"),
                "rarity": raw_result.get("rarity", "Standard"),
                "superpower": raw_result.get("superpower", "Polyvalence"),
                "kryptonite": raw_result.get("kryptonite", "Distraction"),
                "quote": "L'ordre est la forme que l'on donne au chaos."
            }

            # F. Sauvegarde & Injection
            save_lead_to_gsheet(user_email, json.dumps(raw_result), inputs)

            st.session_state['data'] = formatted_data
            st.session_state['analysis_result'] = raw_result
            st.session_state['final_scores'] = final_scores 
            
            # G. Refresh pour afficher le résultat
            st.rerun()



# --- LOGIQUE D'AFFICHAGE (EN DEHORS DU IF SUBMITTED) ---

if 'data' in st.session_state and st.session_state['data']:
    
    # --- DÉBUT DU BLOC INDENTÉ (Tout ce qui suit a 4 espaces ou 1 Tab) ---
    
    # A. Récupération des données
    data = st.session_state['analysis_result']
    formatted_data = st.session_state['data']
    saved_scores = st.session_state.get('final_scores', {})
    
    # B. Séparateur
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Création des 4 onglets de visualisation
    res_tab1, res_tab2, res_tab3, res_tab4 = st.tabs(["📅 Votre Personne", "⚡ Votre Énergie", "🧬 Votre Profil", "⚙️ Votre Mécanique"])

    # ==========================================================================
    # ONGLET 1 : SYNTHÈSE (RPG + RADAR)
    # ==========================================================================
    with res_tab1:
        col_card, col_radar = st.columns([1.3, 1], gap="medium")
        
        with col_card:
            st.markdown(f"""
<div class="rpg-card" style="text-align: left; background-color: #fff; border: 1px solid #e5e5e5; border-radius: 12px; padding: 25px; box-shadow: 0 4px 20px rgba(0,0,0,0.05);">
<div style="display:flex; justify-content:space-between; align-items:center;">
<div style="font-size:11px; color:#111; font-weight:bold; letter-spacing:1px; text-transform:uppercase; border:1px solid #111; padding: 3px 8px; border-radius:4px;">
🧬 Rareté : {data.get('rarity', 'N/A')}
</div>
<div style="font-size:11px; color:#888;">ID: #OCEAN-{random.randint(1000,9999)}</div>
</div>
<div class="archetype-title" style="text-align:left; margin-top:15px; font-size:26px; color:#111; font-weight:900; letter-spacing:-0.5px;">
{data.get('archetype', 'Architecte')}
</div>
<div style="font-style:italic; color:#666; margin-top:5px; font-size:14px; border-left: 3px solid #111; padding-left: 12px;">
"{data.get('quote', 'Pas de citation')}"
</div>
<hr style="border-top: 1px solid #eee; margin: 20px 0;">

<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #eee; margin-bottom: 20px;">
<div style="color:#111; font-weight:bold; font-size:11px; margin-bottom:5px; text-transform:uppercase;">DIAGNOSTIC SYSTÈME :</div>
<div style="color:#555; font-size:13px; line-height:1.5;">
Configuration neuronale atypique détectée. Ce profil présente un potentiel de haute performance bridé par des frictions spécifiques.
</div>
</div>

<div style="margin-bottom: 15px;">
<div style="color:#888; font-size:10px; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px; font-weight:600;">
⚔️ Votre Super-Pouvoir
</div>
<div style="color:#007700; font-weight:bold; font-size:15px; background: #eaffea; padding: 10px; border-radius:6px; border: 1px solid #d4fdd4;">
{data.get('superpower', 'N/A')}
</div>
</div>
<div>
<div style="color:#888; font-size:10px; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px; font-weight:600;">
🔴 Votre Faiblesse (Kryptonite)
</div>
<div style="color:#cc0000; font-weight:bold; font-size:15px; background: #ffebeb; padding: 10px; border-radius:6px; border: 1px solid #ffcdcd;">
{data.get('kryptonite', 'N/A')}
</div>
</div>
</div>
            """, unsafe_allow_html=True)
# st.plotly_chart(fig_radar)
        with col_radar:
            if saved_scores:
                df_scores = pd.DataFrame(dict(r=list(saved_scores.values()), theta=list(saved_scores.keys())))
                fig = px.line_polar(df_scores, r='r', theta='theta', line_close=True, range_r=[0,100])
                fig.update_traces(fill='toself', line_color='#111', line_width=2)
                fig.update_layout(
                    margin=dict(l=20, r=20, t=20, b=20),
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 100], color="#888", showticklabels=False), 
                        angularaxis=dict(color="#111"),
                        bgcolor="rgba(0,0,0,0.02)"
                    ),
                    paper_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # ==========================================================================
    # ONGLET 2 : BIO-RYTHME (Courbe Energie)
    # ==========================================================================
    with res_tab2:
        st.markdown("""
**Analyse du Rythme Biologique :** Ce graphique matérialise votre niveau d'énergie théorique sur la journée. Les pics correspondent aux moments où votre concentration est maximale (idéal pour le travail complexe), tandis que les creux indiquent les périodes de récupération ou de travail superficiel. L'IA se base sur cette courbe pour placer vos tâches les plus difficiles au moment où elles vous coûteront le moins d'effort.
        """)
# st.plotly_chart(fig_energy)
        energy_data = data.get("chart_energy", [])
        if energy_data:
            df_energy = pd.DataFrame(energy_data)
            fig_energy = px.line(df_energy, x="heure", y="niveau", markers=True, line_shape="spline", template="plotly_white")
            fig_energy.update_traces(line_color='#00aa00', line_width=3, marker_size=6, marker_color='#ffffff', marker_line_width=2, marker_line_color='#00aa00')
            fig_energy.add_hline(y=80, line_dash="dot", line_color="#999", annotation_text="Hyperfocus", annotation_position="top left")
            fig_energy.update_layout(
                height=250, 
                xaxis_title=None, 
                yaxis_title=None,
                font=dict(color="#333", size=11),
                hovermode="x unified",
                xaxis=dict(showgrid=False, tickfont=dict(color='#666')),
                yaxis=dict(showgrid=True, gridcolor='#eee', tickfont=dict(color='#666')),
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_energy, use_container_width=True, config={'displayModeBar': False})

    # ==========================================================================
    # ONGLET 3 : MATRICE ÉNERGIE
    # ==========================================================================
    with res_tab3:
        st.markdown("""
**Lecture du Bilan Énergétique :** Ce graphique mesure l'impact biologique réel de chaque tâche sur votre réserve d'énergie mentale. Les barres vertes indiquent vos tâches "Moteur", celles qui correspondent à votre nature profonde et vous procurent de l'élan, tandis que les barres rouges signalent les tâches "Vampires" qui exigent un effort de volonté coûteux. L'IA utilise cette analyse pour équilibrer votre journée, en veillant à ce que les activités régénératrices compensent la dépense nerveuse afin d'éviter l'épuisement.
""")
# st.plotly_chart(fig_matrix, use_container_width=True, config={'displayModeBar': False})
# st.plotly_chart(fig_type_effort)
        matrix_data = data.get("chart_matrix", [])
        if matrix_data:
            df_matrix = pd.DataFrame(matrix_data)
            
            fig_matrix = go.Figure(go.Bar(
                x=df_matrix['impact'],
                y=df_matrix['tache'],
                orientation='h',
                # Texte de la valeur SUR la barre
                text=df_matrix['impact'], 
                textposition='auto',
                marker=dict(
                    color=df_matrix['impact'], 
                    colorscale='RdYlGn', 
                    line=dict(color='rgba(0,0,0,0.1)', width=1)
                )
            ))

            fig_matrix.update_layout(
                height=300, 
                template="plotly_white",
                margin=dict(l=20, r=20, t=30, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                
                xaxis=dict(
                    showgrid=True, 
                    gridcolor='#e0e0e0',
                    zeroline=True,
                    zerolinecolor='#000000', # Ligne zéro noire
                    tickfont=dict(color="#000000", size=12) # Chiffres du bas en noir
                ),
                
                yaxis=dict(
                    autorange="reversed",
                    automargin=True,
                    # C'EST ICI QUE CA SE JOUE :
                    tickfont=dict(color="#000000", size=14, family="Arial, sans-serif", weight="bold") 
                )
            )
            
            st.plotly_chart(fig_matrix, use_container_width=True, config={'displayModeBar': False})

    # ==========================================================================
    # ONGLET 4 : MÉCANIQUE (FOGG)
    # ==========================================================================
    with res_tab4:
        
        # THEORIE CACHÉE
        with st.expander("Comprendre la Mécanique de l'Action (Le Modèle Fogg)", expanded=False):
            
            # --- PARTIE 1 : LE PRINCIPE ---
            st.markdown("#### 1. L'Équation : Pourquoi la volonté ne suffit pas")
            st.markdown("""
            Selon le Dr. B.J. Fogg (Stanford), une action ne se produit pas par magie. Elle est le résultat d'une multiplication stricte entre trois facteurs : la Motivation, la Capacité et le Déclencheur. La règle est impitoyable : si une seule de ces variables est égale à zéro, le résultat est nul. Vous pouvez être extrêmement motivé, si vous n'avez pas de déclencheur, rien ne se passe. À l'inverse, si le déclencheur sonne mais que la tâche est trop difficile pour votre motivation actuelle, vous procrastinez.
            """)

            st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True) # Espaceur
            
        

        st.markdown("""
**Lecture de la Matrice de Résistance :**Ce graphique cartographie vos tâches selon deux dimensions critiques. L'axe horizontal représente la Friction (l'effort d'activation) : plus un point est situé à gauche, plus la tâche est facile à démarrer immédiatement ; à l'inverse, plus il est à droite, plus il demande de discipline. L'axe vertical indique votre Motivation (Dopamine) : les points en haut sont les tâches qui vous excitent, ceux en bas sont celles qui vous ennuient. Cette lecture permet d'identifier visuellement vos "Victoires Rapides" (Haut-Gauche) et d'isoler les zones de "Danger Procrastination" (Bas-Droite) pour ne pas les subir.
        """)
# st.plotly_chart(fig_fogg, use_container_width=True, config={'displayModeBar': False})
# st.plotly_chart(fig_timeline)
        fogg_data = data.get("chart_fogg", [])
        if fogg_data:
            df_fogg = pd.DataFrame(fogg_data)
            
            # 1. Création du graphique
            fig_fogg = px.scatter(
                df_fogg, x="friction", y="dopamine", text="tache", size="importance", color="zone",
                color_discrete_map={"Action": "#2ecc71", "Procrastination": "#e74c3c", "Piège": "#f1c40f"},
                template="plotly_white"
            )
            
            # 2. La ligne de démarcation
            fig_fogg.add_shape(type="line", x0=0, y0=0, x1=100, y1=100, line=dict(color="#bbb", width=2, dash="dot"))
            
            # 3. Optimisation des points (Texte en NOIR)
            fig_fogg.update_traces(
                textposition='top center', 
                textfont=dict(color="#000000", size=11, family="Inter, sans-serif", weight="bold"),
                marker=dict(opacity=0.9, line=dict(width=1, color='#fff'))
            )
            
            # 4. Layout avec FORCAGE des couleurs d'axes
            fig_fogg.update_layout(
                height=350,
                
                # TITRES DES AXES
                xaxis_title="Difficulté (Friction)",
                yaxis_title="Motivation (Dopamine)",
                
                font=dict(family="Inter, sans-serif"),
                margin=dict(l=20, r=20, t=40, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=None, font=dict(color="#000000")),
                
                # --- C'EST ICI QU'ON FORCE LE NOIR ---
                xaxis=dict(
                    showgrid=True, 
                    gridcolor='#e0e0e0', 
                    range=[-5, 105],
                    
                    # Titre de l'axe (Abscisse)
                    title_font=dict(color="#000000", size=14, weight="bold"),
                    # Chiffres de l'axe
                    tickfont=dict(color="#000000", size=12)
                ),
                
                yaxis=dict(
                    showgrid=True, 
                    gridcolor='#e0e0e0', 
                    range=[-5, 105],
                    
                    # Titre de l'axe (Ordonnée)
                    title_font=dict(color="#000000", size=14, weight="bold"),
                    # Chiffres de l'axe
                    tickfont=dict(color="#000000", size=12)
                )
            )
            
            st.plotly_chart(fig_fogg, use_container_width=True, config={'displayModeBar': False})
            
    

    # --------------------------------------------------------------------------
    # 4. LA ZONE PAYWALL (MONEY ZONE)
    # --------------------------------------------------------------------------
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # --- A. L'ANALYSE TEXTE (LE TEASING) ---
    real_analysis = formatted_data.get('analysis_report', "<p>Analyse en cours...</p>")
    
    st.markdown("### 🔓 Extrait de votre Mode d'Emploi")
    
    # On affiche le texte avec le dégradé blanc (Fade Out)
    st.markdown(f"""
<div class="paywall-card" style="position: relative; overflow: hidden; max-height: 280px; padding-bottom: 0; margin-bottom: 40px;">
<div style="color: #1a1a1a; font-size: 16px; line-height: 1.7; text-align: justify;">
{real_analysis}
<br>
<p><strong>[...LA SUITE DE L'ANALYSE EST RÉSERVÉE...]</strong></p>
</div>
<div style="
position: absolute; bottom: 0; left: 0; width: 100%; height: 180px; 
background: linear-gradient(to bottom, rgba(255,255,255,0) 0%, rgba(255,255,255,1) 70%);
z-index: 2; pointer-events: none;">
</div>
</div>
    """, unsafe_allow_html=True)

    # --- SECTION PLANNING (TIMELINE 80/20) ---
    # 1. VÉRIFICATION : Est-ce qu'on a bien reçu le planning ?
# 1. PARTIE PLANNING (S'affiche seulement si les données sont là)
    if "preview_day" in data:
        st.markdown("### 🗓️ Optimisation de votre journée selon le 80/20")
        st.caption(f"Architecture synchronisée pour le profil : {formatted_data.get('archetype', 'Non défini')}")
        st.markdown("<br>", unsafe_allow_html=True)

        for bloc in data["preview_day"]:
            heure = bloc.get("time", "--:--")
            phase = bloc.get("phase", "Bloc non défini")
            tag = bloc.get("tag_visible", "Focus")
            secret = bloc.get("neuro_logic", "Contenu réservé...")

            # On affiche la timeline
            st.markdown(f"""
            <div class="timeline-row">
                <div class="time-col">{heure}</div>
                <div class="card-col">
                    <div class="card-title">
                        {phase}
                        <span style="font-size: 0.75rem; color: #2E7D32; background: #E8F5E9; padding: 4px 10px; border-radius: 12px; margin-left: 10px; vertical-align: middle; font-weight: 600;">
                            {tag}
                        </span>
                    </div>
                    <div class="blur-content" style="margin-top: 8px; line-height: 1.5;">
                        {secret}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)


    # 2. PARTIE CARTE DE PAIEMENT (S'affiche TOUJOURS à la fin)
    # Astuce : On met le HTML dans une variable collée à gauche pour éviter les bugs
    st.markdown(f"""
    <div style="
    width: 100%;
    max-width: 450px;
    margin: 40px auto; 
    background: #ffffff;
    border: 1px solid #e0e0e0;
    box-shadow: 0 10px 40px rgba(0,0,0,0.08);
    border-radius: 20px;
    padding: 30px;
    text-align: center;">

    <div style="font-size: 40px; margin-bottom: 10px;">🔐</div>

    <h3 style="color: #111; font-weight: 900; margin: 0 0 10px 0; font-size: 22px;">
    Débloquez votre Architecture
    </h3>

    <p style="color: #666; font-size: 14px; margin-bottom: 25px; line-height: 1.5;">
    Accédez à votre analyse complète, vos graphiques et votre <strong>Planning Neuro-Ergonomique</strong> détaillé.
    </p>

    <a href="{STRIPE_LINK}" target="_blank" style="
    display: block;
    width: 100%;
    background-color: #111;
    color: #fff;
    font-weight: 700;
    padding: 16px 0;
    border-radius: 12px;
    text-decoration: none;
    font-size: 16px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    transition: transform 0.2s ease;">
    OBTENIR MON DOSSIER (9.90€)
    </a>

    <div style="margin-top: 15px; font-size: 11px; color: #999; display: flex; justify-content: center; gap: 15px;">
    <span>🔒 Paiement Sécurisé</span>
    <span>⚡ Accès Immédiat</span>
    </div>
    </div>
    <div style="height: 50px;"></div> 
    """, unsafe_allow_html=True)