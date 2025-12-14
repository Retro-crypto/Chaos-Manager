import streamlit as st
import json
import pandas as pd
import random
import plotly.express as px
import plotly.graph_objects as go # Pour les graphiques avancés
from backend import parse_schedule, generate_ics_file
st.set_page_config(page_title="Chaos Manager V5", page_icon="🧠", layout="wide")

# --- CSS & STYLE ---
st.markdown("""
<style>
    /* --- GENERAL SETTINGS --- */
    .stApp { 
        background-color: #0e1117; 
        font-family: 'Inter', sans-serif;
    }
    
    /* --- LE BOUTON D'ACTION --- */
    .stButton > button {
        background: linear-gradient(90deg, #FF4B4B 0%, #CE2424 100%);
        color: white;
        border: none;
        padding: 15px 30px;
        font-size: 18px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.4);
        transition: all 0.3s ease;
        width: 100%;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 75, 75, 0.6);
        background: linear-gradient(90deg, #FF6B6B 0%, #E03434 100%);
    }

    /* --- RADIO BUTTONS : GRID FULL WIDTH (Le Fix) --- */
    
    /* 1. Le Conteneur Principal : C'est LUI qui décide de la largeur */
    div[role="radiogroup"] {
        display: grid !important;
        /* auto-fit + 1fr = Occupe TOUT l'espace disponible */
        grid-template-columns: 1fr !important;
        gap: 15px !important;
        width: 100% !important; /* Force l'étalement total */
    }

    /* 2. Les Cartes (Tuiles) */
    div[role="radiogroup"] > label {
        background-color: #161924 !important;
        border: 1px solid #333 !important;
        padding: 20px !important;
        border-radius: 12px !important;
        margin: 0 !important;
        transition: all 0.2s ease !important;
        
        /* Force la carte à remplir sa cellule de grille */
        width: 100% !important; 
        height: 100% !important;
        min-height: 120px !important; /* Hauteur minimale uniforme */
        
        /* Centrage du contenu */
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
    }
    
    /* 3. Effet Survol */
    div[role="radiogroup"] > label:hover {
        border-color: #FF4B4B !important;
        background-color: #1a1d2b !important;
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 2;
    }

    /* 4. Sélection */
    div[role="radiogroup"] > label[data-checked="true"] {
        border-color: #FF4B4B !important;
        background-color: rgba(255, 75, 75, 0.08) !important;
        box-shadow: 0 0 15px rgba(255, 75, 75, 0.1);
    }

    /* 5. Typographie */
    div[role="radiogroup"] label p {
        font-weight: 800 !important;
        font-size: 16px !important;
        color: #fff !important;
        margin-bottom: 5px !important;
    }
    
    div[role="radiogroup"] label span {
        font-size: 12px !important;
        color: #888 !important;
        line-height: 1.3 !important;
    }

    /* --- AUTRES ELEMENTS --- */
    .stTextArea textarea {
        background-color: #161924 !important;
        border: 1px solid #2b3042 !important;
        border-radius: 8px !important;
        color: #e0e0e0 !important;
    }
    .stTextArea textarea:focus {
        border-color: #FF4B4B !important;
        box-shadow: 0 0 8px rgba(255, 75, 75, 0.2) !important;
    }
    .stTextArea label {
        color: #888 !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #13151b !important;
        border: 1px solid #333 !important;
        border-radius: 10px !important;
        padding: 20px !important;
        margin-bottom: 20px;
    }
    
    /* --- ELEMENTS SPECIFIQUES --- */
    .concept-box { background: linear-gradient(180deg, #13151b 0%, #0e1117 100%); border-left: 4px solid #FF4B4B; padding: 20px; border-radius: 0 12px 12px 0; border: 1px solid #222; margin-bottom:30px; }
    .profile-example { background-color: #1c202a; padding: 20px; border-radius: 12px; text-align: center; border: 1px solid #333; font-size: 13px; }
    .tech-badge { background-color: rgba(28, 32, 42, 0.8); border: 1px solid #00ff00; color: #00ff00; padding: 4px 10px; border-radius: 4px; font-family: monospace; font-size: 11px; font-weight: bold; }
    
    .rpg-card { background: linear-gradient(145deg, #1e2330 0%, #13151b 100%); border: 1px solid #444; border-radius: 16px; padding: 25px; text-align: center; position: relative; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .rpg-card::before { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 1px; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent); }
    .archetype-title { color: #FF4B4B; font-size: 28px; font-weight: 800; text-transform: uppercase; margin-top: 10px; text-shadow: 0 0 20px rgba(255, 75, 75, 0.3); }
    
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #161924; border-radius: 4px 4px 0 0; border: 1px solid #333; border-bottom: none; color: #888; padding: 10px 20px; }
    .stTabs [aria-selected="true"] { background-color: #FF4B4B !important; color: white !important; font-weight: bold; }

    .blur-text { filter: blur(6px); user-select: none; color: #666; opacity: 0.6; }
    .locked-section { border: 1px dashed #FF4B4B; padding: 30px; border-radius: 16px; background: rgba(255, 75, 75, 0.05); text-align: center; margin-top: 30px; }

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
# --- FORMULAIRE ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("##### Remplis ce formulaire. L'IA va sélectionner les 'Secret Prompts' adaptés à tes scores.")




with st.form("psycho_form"):
    
    # --- BLOC THEORIE : OCEAN & METABOLISME DU TRAVAIL ---
    
    # 1. LE POSTULAT SCIENTIFIQUE
    with st.container(border=True):
        st.markdown('<div style="color:#00ff00; font-weight:bold; margin-bottom:10px;">🧪 1. Le "Hardware" Cognitif (Big Five vs MBTI)</div>', unsafe_allow_html=True)
        
        c_theo, c_eq = st.columns([2, 1], gap="large")
        
        with c_theo:
            st.markdown("""
            **Pourquoi le MBTI ne suffit pas :**
            Le MBTI vous met dans des "boîtes" (ex: INTJ). La science (Big Five/OCEAN) vous place sur des **spectres continus**. 
            
            Un agenda échoue souvent non pas par manque de volonté, mais par **Dissonance Cognitive** : vous essayez d'appliquer une structure rigide (Haute Conscience) à un cerveau divergent (Haute Ouverture).
            
            **Notre Approche :**
            Nous ne jugeons pas votre personnalité. Nous mesurons vos **Coûts Cognitifs** pour aligner la méthode sur votre biologie.
            """)
        
        with c_eq:
            # On remplace la division illogique par une soustraction (Distance/Écart)
            st.latex(r"Friction = | Cerveau - Agenda |")
            st.caption("L'épuisement vient de l'écart (Δ) entre votre nature et vos tâches.")

    # 2. LES 3 VECTEURS D'IMPACT SUR LE TRAVAIL
    with st.container(border=True):
        st.markdown('<div style="color:#FF4B4B; font-weight:bold; margin-bottom:15px;">⚙️ 2. Comment vos traits dictent votre Planning</div>', unsafe_allow_html=True)
        
        col_struct, col_social, col_stress = st.columns(3, gap="medium")
        
        # --- COLONNE 1 : STRUCTURE ---
        with col_struct:
            st.markdown("#### 📐 Input (O + C)")
            st.caption("Traitement de l'Information")
            st.markdown("""
            **Le Conflit : Innovation vs Rigueur**
            
            Si votre **Ouverture (O)** est élevée, la routine tue votre productivité car vous avez besoin de nouveauté. À l'inverse, une **Conscience (C)** forte exige des plans détaillés car l'improvisation génère de l'angoisse.
            
            **👉 Impact Agenda :** L'IA arbitrera dynamiquement pour générer soit des blocs séquentiels rigides (Mode Architecte), soit des sprints aléatoires (Mode Chaos).
            """)

        # --- COLONNE 2 : ÉNERGIE ---
        with col_social:
            st.markdown("#### ⚡ Fuel (E + A)")
            st.caption("Dynamique d'Interaction")
            st.markdown("""
            **Le Conflit : Groupe vs Solo**
            
            Une **Extraversion (E)** élevée signifie que le silence vous draine et que vous rechargez vos batteries en réunion. Cependant, une haute **Agréabilité (A)** pose un risque opérationnel : la difficulté à dire non cannibalise votre temps de travail.
            
            **👉 Impact Agenda :** L'IA placera les tâches collaboratives sur vos pics d'énergie et verrouillera des créneaux "Forteresse" pour protéger votre concentration.
            """)

        # --- COLONNE 3 : RÉSILIENCE ---
        with col_stress:
            st.markdown("#### 🌪️ Sécurité (N)")
            st.caption("Gestion de la Charge")
            st.markdown("""
            **Le Conflit : Vigilance vs Calme**
            
            Un **Névrosisme (N)** élevé implique une forte sensibilité au stress (Cortisol) : une erreur mineure ou un imprévu peut paralyser votre journée. Un profil bas (Stoïque) restera hermétique à la pression.
            
            **👉 Impact Agenda :** Pour les profils sensibles, le système injectera impérativement des "Buffers" (pauses de sécurité) entre les tâches lourdes pour éviter la surchauffe.
            """)
    
    # --- SECTION UNIQUE : CALIBRATION (FUSION TAB 1 & 2) ---
    
    st.markdown("---")
    st.markdown("#### 1. Calibration Neuro-Psychologique")
    
    st.info("""
    ℹ️ **Protocole de Saisie :** Si vous avez vos scores OCEAN officiels, reportez-les. 
    Sinon, ajustez les curseurs selon votre **ressenti honnête**. Il n'y a pas de "bon" score, seulement un alignement nécessaire.
    """)

    # Layout en 2 colonnes
    col_brain, col_heart = st.columns(2, gap="medium")

    # --- COLONNE GAUCHE : TRAITEMENT INFO ---
    with col_brain:
        st.markdown("##### 🧠 Le Cerveau (Traitement de l'Info)")
        
        # O - OUVERTURE
        with st.container(border=True):
            st.markdown("**🌊 1. Ouverture (O)**")
            st.markdown("""
            <div style="font-size:14px; line-height:1.4; color:#ddd; margin-bottom:10px;">
            Ce trait mesure votre appétit pour l'abstraction. Un score élevé indique un besoin vital de nouveauté intellectuelle (ex: tester un nouvel outil chaque semaine). Un score bas révèle une préférence pour les méthodes éprouvées et l'efficacité pragmatique.
            </div>
            """, unsafe_allow_html=True)
            o_score = st.slider("O", 0, 100, 50, key="slider_o", label_visibility="collapsed")
            st.markdown('<div style="font-size:11px; color:#888; display:flex; justify-content:space-between;"><span>🛡️ Pragmatique</span><span>Explorateur 🚀</span></div>', unsafe_allow_html=True)

        # C - CONSCIENCE
        with st.container(border=True):
            st.markdown("**📐 2. Conscience (C)**")
            st.markdown("""
            <div style="font-size:14px; line-height:1.4; color:#ddd; margin-bottom:10px;">
            C'est le métronome de votre autodiscipline. Une haute conscience se traduit par une planification millimétrée (ex: préparer sa "To-Do" la veille). Une conscience basse fonctionne à l'impulsion et brille dans l'urgence, mais déteste les structures rigides.
            </div>
            """, unsafe_allow_html=True)
            c_score = st.slider("C", 0, 100, 50, key="slider_c", label_visibility="collapsed")
            st.markdown('<div style="font-size:11px; color:#888; display:flex; justify-content:space-between;"><span>🎨 Spontané</span><span>Architecte 🏗️</span></div>', unsafe_allow_html=True)

        # E - EXTRAVERSION
        with st.container(border=True):
            st.markdown("**⚡ 3. Extraversion (E)**")
            st.markdown("""
            <div style="font-size:14px; line-height:1.4; color:#ddd; margin-bottom:10px;">
            Il s'agit de votre système de recharge énergétique. Pour un extraverti, l'interaction sociale est un carburant qui stimule la réflexion. Pour un introverti, le monde extérieur est un coût : l'isolement est nécessaire pour régénérer ses batteries mentales.
            </div>
            """, unsafe_allow_html=True)
            e_score = st.slider("E", 0, 100, 50, key="slider_e", label_visibility="collapsed")
            st.markdown('<div style="font-size:11px; color:#888; display:flex; justify-content:space-between;"><span>🔋 Deep Worker</span><span>Connecteur 🗣️</span></div>', unsafe_allow_html=True)

    # --- COLONNE DROITE : GESTION EMOTION ---
    with col_heart:
        st.markdown("##### ❤️ Le Coeur (Régulation)")

        # A - AGREABILITÉ
        with st.container(border=True):
            st.markdown("**🤝 4. Agréabilité (A)**")
            st.markdown("""
            <div style="font-size:14px; line-height:1.4; color:#ddd; margin-bottom:10px;">
            Ce curseur définit votre rapport à la négociation. Une forte agréabilité privilégie l'harmonie du groupe et le consensus (ex: dire oui pour aider). Un score faible signale un esprit de compétition froid, capable de trancher dans le vif sans émotion.
            </div>
            """, unsafe_allow_html=True)
            a_score = st.slider("A", 0, 100, 50, key="slider_a", label_visibility="collapsed")
            st.markdown('<div style="font-size:11px; color:#888; display:flex; justify-content:space-between;"><span>⚔️ Challenger</span><span>Diplomate 🕊️</span></div>', unsafe_allow_html=True)

        # N - NÉVROSISME
        with st.container(border=True):
            st.markdown("**🌪️ 5. Névrosisme (N)**")
            st.markdown("""
            <div style="font-size:14px; line-height:1.4; color:#ddd; margin-bottom:10px;">
            C'est votre thermostat de gestion du stress. Un profil "Sentinelle" (score élevé) anticipe le pire et détecte la moindre erreur, ce qui coûte cher en énergie. Un profil "Stoïque" reste imperméable à la pression, conservant son sang-froid même dans le chaos.
            </div>
            """, unsafe_allow_html=True)
            n_score = st.slider("N", 0, 100, 50, key="slider_n", label_visibility="collapsed")
            st.markdown('<div style="font-size:11px; color:#888; display:flex; justify-content:space-between;"><span>🗿 Stoïque</span><span>Sentinelle 🚨</span></div>', unsafe_allow_html=True)




    # --- DEBUT DU BLOC : CALIBRATION SOFTWARE ---
    st.markdown("---")
    st.markdown("#### 2. Calibration du 'Software' (Mécanique de Travail)")
    
    # --- MODULE 1 : RYTHME CIRCADIEN ---
    with st.container(border=True):
        st.markdown('<div style="color:#4DA6FF; font-weight:bold; font-size:16px; margin-bottom:15px;">🦁 Module 1 : Synchronisation (Biorythme)</div>', unsafe_allow_html=True)
        
        # LAYOUT : 1/3 (Choix) vs 2/3 (Théorie)
        c_input, c_theory = st.columns([1, 2], gap="large")
        
        with c_input:
            st.markdown("**SÉLECTION DU PROFIL**")
            st.caption("Identifiez votre phénotype selon votre courbe d'énergie naturelle.")
            
            chronotype = st.radio(
            "Chronotype", 
            [
                "🦁 **Lion (Matin)** : Ce profil se caractérise par un pic de cortisol très précoce vers 6h du matin, entraînant une performance linéaire décroissante qui rend tout travail complexe inefficace après 15h.",
                "🐻 **Ours (Solaire)** : Ce profil reste strictement synchronisé sur le cycle solaire, avec un pic de vigilance maximal situé entre 10h et 14h nécessitant une nuit complète de 8h de sommeil monophasique.",
                "🐺 **Loup (Soir)** : Ce profil subit une phase biologique retardée qui provoque une lourde inertie matinale, décalant son pic cognitif et créatif vers la plage horaire de 17h à minuit.",
                "🐬 **Dauphin (Chaos)** : Ce profil présente une architecture de sommeil fragmentée couplée à un cortisol chroniquement élevé, l'obligeant à exploiter des fenêtres d'efficacité erratiques et imprévisibles."
            ], 
            label_visibility="collapsed"
        )
        
        with c_theory:
            st.info("🧬 **Théorie : Chronobiologie & Architecture Temporelle**")
            
            st.markdown("""
            #### 1. Le Mécanisme (Le "Tug-of-War" Hormonal)
            La performance cognitive n'est pas une question de volonté, mais le résultat d'une équation vectorielle régie par l'hypothalamus (Noyau Suprachiasmatique). Deux forces s'opposent en permanence :
            
            D'un côté, le **Processus C (Circadien)** agit comme votre horloge interne. Génétiquement déterminé, il sécrète le cortisol pour l'éveil selon une courbe sinusoïdale. De l'autre, le **Processus S (Homéostatique)** représente la pression de sommeil qui s'accumule via l'adénosine dans le cerveau au fil des heures. Le "Deep Work" n'est possible que lorsque l'écart entre ces deux courbes est maximal.
            
            ---
            
            #### 2. La Réalité Évolutive (Pourquoi 4 profils ?)
            Cette diversité n'est pas un hasard, mais une stratégie de survie tribale ("Sentinel Theory"). Pour qu'un groupe survive aux prédateurs, il fallait une vigilance rotative sur 24h : les Lions gardaient l'aube, les Loups le crépuscule, et les Dauphins assuraient une veille légère et erratique.
            
            **L'Origine du Modèle :**
            Cette classification a été théorisée par le **Dr. Michael Breus** (Psychologue Clinicien) pour une raison précise : ses patients n'étaient pas malades, ils étaient juste mal calés. Il a conçu ce système pour ceux qui, comme vous peut-être, se sentent coupables de ne pas être performants à 8h du matin. Il a brisé le mythe binaire "Lève-tôt / Lève-tard" pour offrir un mode d'emploi adapté à la réalité biologique de chacun.
            
            **Le Problème Moderne :** La société industrielle a standardisé le travail sur le rythme des Ours (55% de la population). Ce dogme du "9h-17h" impose aux profils atypiques (Loups et Dauphins) un **Jetlag Social** permanent. Lutter contre son chronotype transforme votre cortisol en toxine, réduisant votre QI fluide et augmentant l'inflammation systémique.
            
            > **Axiome :** Ne cherchez pas à réparer votre horloge, changez l'heure de vos tâches.
            """)

    # --- MODULE 2 : ARCHITECTURE ---
    with st.container(border=True):
        st.markdown('<div style="color:#FF4B4B; font-weight:bold; font-size:16px; margin-bottom:15px;">📐 Module 2 : Type d\'Architecture (Mode Cognitif)</div>', unsafe_allow_html=True)
        
        c_input, c_theory = st.columns([1, 2], gap="large")
        
        with c_input:
            st.markdown("**TYPE D'INTERVENTION**")
            st.caption("Sélectionnez le registre neuronal sollicité par la tâche.")
            
            arch_type = st.radio(
                "Architecture", 
                [
                    "🛠️ **Technique (Hard)** : Mode de pensée convergent et algorithmique. Exige une isolation sensorielle totale pour résoudre des problèmes à solution unique (Code, Math, Infra) avec une tolérance zéro à l'ambiguïté.",
                    "⚖️ **Éthique (Soft)** : Mode de pensée dialectique et nuancé. Mobilise l'intelligence émotionnelle et culturelle pour traiter des dilemmes humains où la logique binaire est inopérante (Négociation, Valeurs, Politique).",
                    "🌀 **Système (Meta)** : Mode de pensée holistique et architectural. Vise à réduire l'entropie globale du système en connectant des concepts disparates (Design Pattern, Stratégie, Philosophie) via des boucles de rétroaction."
                ], 
                label_visibility="collapsed"
            )
            
        with c_theory:
            st.info("🏗️ **Théorie : L'Orthogonalité & La Dette de Commutation**")
            
            st.markdown("""
            #### 1. Le Mécanisme (L'Inertie Neurale)
            Contrairement à un processeur informatique, votre cerveau ne pratique pas le "Multitasking", mais le "Task-Switching". Le problème est que chaque bascule entre un mode logique (froid) et un mode empathique (chaud) engendre une **Taxe Cognitive**. Votre cerveau doit "décharger" le contexte précédent pour "charger" le nouveau, consommant du glucose à vitesse grand V.
            
            ---
            
            #### 2. L'Origine du Concept (Le "Résidu d'Attention")
            En 2009, la chercheuse **Sophie Leroy** (University of Minnesota) a identifié pourquoi vous vous sentez épuisé après une journée hachée, même sans travail intense. Elle a théorisé le **"Attention Residue"** : lorsque vous passez d'un code Python à une réunion RH, une partie de vos ressources cognitives reste "bloquée" en arrière-plan sur la tâche A.
            
            **Le Conflit Neurologique :**
            C'est une guerre de territoires. Le mode "Hard" active le Cortex Préfrontal Dorso-Latéral (Logique binaire), qui *inhibe* le Système Limbique pour fonctionner. À l'inverse, le mode "Soft" nécessite l'activation émotionnelle. Tenter d'alterner les deux, c'est comme demander à une voiture de passer la marche arrière en pleine autoroute. La friction n'est pas psychologique, elle est mécanique.
            
            **La Solution :** L'étanchéité. Grouper les tâches par signature neurologique (Batching) est le seul moyen de supprimer cette taxe.
            
            > **Axiome :** On ne répare pas un moteur avec de la compassion, et on ne dirige pas une équipe avec un algorithme.
            """)
    # --- MODULE 3 : WORKING GENIUS ---
    with st.container(border=True):
        st.markdown('<div style="color:#00ff00; font-weight:bold; font-size:16px; margin-bottom:15px;">⚙️ Module 3 : Moteur d\'Exécution (Topologie de l\'Effort)</div>', unsafe_allow_html=True)
        
        c_input, c_theory = st.columns([1, 2], gap="large")
        
        with c_input:
            st.markdown("**ZONE DE FRICTION**")
            st.caption("Où se situe votre blocage énergétique actuel ?")
            
            work_genius = st.radio(
                "Génie", 
                [
                    "✨ **Idéation (Invention)** : Phase de divergence et de haute entropie. Vous excellez à générer des concepts *ex nihilo* et à identifier les problèmes, mais l'obligation de structurer ou de finir vous paralyse.",
                    "🔥 **Activation (Mise en Orbite)** : Phase de transition cinétique. Vous excellez à vaincre l'inertie de départ pour transformer une idée abstraite en projet concret, mais la maintenance routinière vous insupporte.",
                    "🏗️ **Finition (Ténacité)** : Phase de convergence et de réduction d'entropie. Vous excellez à pousser le projet à travers les derniers 20% de friction pour livrer un produit fini, mais la feuille blanche vous angoisse."
                ], 
                label_visibility="collapsed"
            )
            
        with c_theory:
            st.info("⚡ **Théorie : La Thermodynamique de l'Effort (Modèle Lencioni)**")
            
            st.markdown("""
            #### 1. Le Mécanisme (Altitude et Gravité)
            Tout travail obéit à une loi physique de transformation d'énergie. Une tâche ne naît pas finie ; elle doit descendre une **Courbe d'Altitude**. Elle commence dans la stratosphère (30 000 pieds), là où l'air est rare et la vision infinie (Le *Pourquoi*). Elle doit ensuite traverser la zone de turbulence (15 000 pieds) pour vaincre l'inertie et s'organiser (Le *Comment*), avant d'atterrir sur le tarmac rugueux de la réalité pour être livrée (Le *Quoi*).
            
            ---
            
            #### 2. L'Origine du Diagnostic (La "Compétence sans Joie")
            Le consultant **Patrick Lencioni** a découvert une anomalie récurrente : des cadres ultra-compétents qui faisaient des burnout sans surcharge de travail. Sa conclusion a changé la donne : l'épuisement ne vient pas de l'intensité de l'effort, mais de la **nature de l'effort**.
            
            **Le Coût de la Mésentente :**
            Chaque cerveau possède un "Génie" (qui recharge l'énergie) et une "Frustration" (qui la draine). Le drame organisationnel est d'assigner un profil "Aérien" (Idéateur) au polissage des détails au sol, ou de demander à un profil "Terrestre" (Finisseur) de voler sans plan de vol. Cette friction génère une chaleur inutile : c'est la source mécanique de la procrastination. Ce n'est pas de la paresse, c'est un moteur qui tourne avec le mauvais carburant.
            
            > **Diagnostic :** Si vous ressentez une fatigue lourde *avant même* de commencer, c'est que la tâche sollicite votre zone de frustration naturelle.
            """)

# --- SECTION 3 : LE CIBLAGE STRATÉGIQUE (Remplacement Complet) ---
    st.markdown("---")
    st.markdown("#### 3. La War Room : Contexte & Objectifs")

    # CONTENEUR PRINCIPAL
    with st.container(border=True):
        
        # 1. LE VECTEUR D'INTENSITÉ (PHASE DE VIE)
        st.markdown('<div style="color:#FF4B4B; font-weight:bold; margin-bottom:10px;">🌡️ Étape 1 : Calibrer l\'Intensité (Phase de Vie)</div>', unsafe_allow_html=True)
        st.caption("Un planning de temps de paix ne fonctionne pas en temps de guerre. Où en êtes-vous ?")
        
        life_phase = st.radio(
            "Phase de Vie",
            [
                "🔥 **War Time (Survie/Deadline)** : Urgence absolue. Je sacrifie le confort pour l'objectif. Sommeil optimisé, zéro distraction, focus unique. C'est un sprint.",
                "🏗️ **Builder (Construction)** : Création de valeur long terme (Lancer un projet, écrire). Je nécessite des blocs profonds (Deep Work) le matin et de la gestion l'après-midi.",
                "⚖️ **Maintenance (Équilibre)** : Gestion du quotidien (Salarié, Parents). Je cherche à optimiser le ratio effort/résultat sans m'épuiser. Time-boxing strict 9h-18h.",
                "🌱 **Recovery (Récupération)** : Post-Burnout ou Vacances. Priorité à la santé mentale et au sommeil. Je veux réduire la charge cognitive au minimum."
            ],
            label_visibility="collapsed"
        )
        
        st.markdown("---")

        # 2. LE CIBLAGE (MISSION & TEMPS)
        st.markdown('<div style="color:#00ff00; font-weight:bold; margin-bottom:10px;">🎯 Étape 2 : Définir la Cible (Mission & Logistique)</div>', unsafe_allow_html=True)
        
        c_mission, c_time = st.columns([2, 1], gap="medium")
        
        with c_mission:
            mission = st.text_input(
                "La North Star (Objectif Unique)", 
                placeholder="Ex: Terminer la V1 du code Python...",
                help="Si vous ne deviez faire qu'une seule chose aujourd'hui pour être fier de vous, ce serait quoi ?"
            )
        
        with c_time:
            time_range = st.slider(
                "Plage d'Activation",
                min_value=0, max_value=24, value=(8, 20),
                format="%dh"
            )
            st.caption(f"Amplitude : {time_range[1] - time_range[0]}h de disponibilité.")

        st.markdown("---")

        # 3. LE DIAGNOSTIC DE FRICTION (POURQUOI L'ÉCHEC ?)
        st.markdown('<div style="color:#4DA6FF; font-weight:bold; margin-bottom:10px;">🚧 Étape 3 : Identifier l\'Ennemi (Frictions)</div>', unsafe_allow_html=True)
        
        col_frict_1, col_frict_2 = st.columns(2)
        
        with col_frict_1:
            st.markdown("**Interne (Ce qui vient de vous)**")
            friction_internal = st.multiselect(
                "Blocages Internes",
                [
                    "⚡ Démarrage (Procrastination)",
                    "🤯 Brouillard Mental (Fatigue)",
                    "✨ Perfectionnisme (Peur de finir)",
                    "🦋 Papillonnage (Manque de Focus)",
                    "📉 Baisse de Dopamine (Ennui)"
                ],
                label_visibility="collapsed"
            )
            
        with col_frict_2:
            st.markdown("**Externe (Ce qui vient des autres)**")
            friction_external = st.multiselect(
                "Blocages Externes",
                [
                    "🔔 Notifications / Smartphone",
                    "🗣️ Interruptions (Collègues/Famille)",
                    "📝 Tâches imprévues",
                    "🔊 Environnement Bruyant"
                ],
                label_visibility="collapsed"
            )

    # BOUTON D'ACTION
    st.markdown("<br>", unsafe_allow_html=True)
    submitted = st.form_submit_button("🚀 GÉNÉRER LE PROTOCOLE TACTIQUE", type="primary", use_container_width=True)
    
    submitted = st.form_submit_button("🚀 LANCER L'ANALYSE NEURO-CROSS", type="primary", use_container_width=True)
    



# --- LOGIQUE DE SOUMISSION ---
if submitted:
    # 1. Consolidation des Scores
    final_O = o_score if o_score > 0 else o_est
    final_C = c_score if c_score > 0 else c_est
    final_E = e_score if e_score > 0 else e_est
    final_A = a_score if a_score > 0 else a_est
    final_N = n_score if n_score > 0 else n_est
    
    final_scores = {
        "Ouverture": final_O, "Conscience": final_C, 
        "Extraversion": final_E, "Agréabilité": final_A, "Névrosisme": final_N
    }

    # 2. Calcul de la Tendance
    if final_C >= 75:
        tendency = "ARCHITECTE (Structure Rigide)"
    elif final_C <= 30:
        tendency = "CHAOS PILOT (Fonctionnement par Sauts)"
    else:
        tendency = "HYBRIDE (Flexibilité Modérée)"

    # 3. Validation
    if not mission and not blockers:
        st.warning("⚠️ Mission ou Blocage requis pour triangulation.")
        st.stop()

    # 4. Construction de la Payload
    inputs = {
        "scores": final_scores,
        "work_style": {
            "chronotype": chronotype,
            "architecture": arch_type,
            "genius": work_genius,
            "tendency": tendency
        },
        "context": {
            "mission": mission,
            "routine": routine,
            "blockers": blockers
        }
    }

    # 5. Exécution & Stockage
    with st.spinner("🔄 Initialisation du Core Gemini..."):
        # Appel simple sans argument debug_mode
        raw_response = parse_schedule(inputs) 
        
        try:
            # Stockage dans la mémoire de session
            st.session_state['analysis_result'] = json.loads(raw_response)
            # On sauvegarde aussi les scores pour le Paywall
            st.session_state['final_scores'] = final_scores 
            st.session_state['tendency'] = tendency
        except json.JSONDecodeError:
            st.error("🚨 Erreur Critique : Format invalide reçu du backend.")
            st.code(raw_response)
            st.stop()

# --- LOGIQUE D'AFFICHAGE (EN DEHORS DU IF SUBMITTED) ---
# Ce bloc doit être COLLÉ À GAUCHE (Indentation 0)
if 'analysis_result' in st.session_state:
    
    # On récupère les données
    data = st.session_state['analysis_result']
    # On récupère les scores sauvegardés pour éviter les erreurs d'affichage
    saved_scores = st.session_state.get('final_scores', {"Conscience": 50}) 
    saved_tendency = st.session_state.get('tendency', "Inconnu")

    # --- RÉSULTATS ---
    st.markdown("---")
    
    # Création des 4 onglets de visualisation
    res_tab1, res_tab2, res_tab3, res_tab4 = st.tabs(["📅 Synthèse & Planning", "⚡ Bio-Rythme", "🧬 Matrice Énergie", "⚙️ Mécanique de l'Action"])

    # --- ONGLET 1 : SYNTHÈSE & PLANNING ---
    with res_tab1:
        st.markdown("#### 📅 L'Algorithme de Structuration Temporelle")

        # BLOC 1 : LA STRUCTURE COGNITIVE (Conscience)
        with st.container(border=True):
            st.markdown('<div style="color:#00ff00; font-weight:bold; margin-bottom:10px;">📐 1. L\'Axe de la Structure (Conscience)</div>', unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3, gap="medium")
            
            with c1:
                st.markdown("**🔼 L'Architecte (C > 75)**")
                st.caption("Besoin : Continuité")
                st.success("Stratégie : SÉQUENTIEL")
                st.markdown("Performance via la prévisibilité.<br><b>🔧 Action :</b> Deep Work massif (90min).", unsafe_allow_html=True)

            with c2:
                st.markdown("**⏺️ Le Flex-Master (30-75)**")
                st.caption("Besoin : Équilibre")
                st.warning("Stratégie : HYBRIDE")
                st.markdown("Cadre souple requis.<br><b>🔧 Action :</b> Matin Carré / Aprèm Libre.", unsafe_allow_html=True)
                
            with c3:
                st.markdown("**🔽 Le Chaos Pilot (C < 30)**")
                st.caption("Besoin : Urgence")
                st.error("Stratégie : SPRINT")
                st.markdown("Moteur dopamine/nouveauté.<br><b>🔧 Action :</b> Gamification (25min).", unsafe_allow_html=True)

        # BLOC 2 : LA CHARGE MENTALE (Névrosisme)
        with st.container(border=True):
            st.markdown('<div style="color:#FF4B4B; font-weight:bold; margin-bottom:10px;">🧠 2. L\'Axe de la Charge (Névrosisme)</div>', unsafe_allow_html=True)
            
            n1, n2, n3 = st.columns(3, gap="medium")
            
            with n1:
                st.markdown("**🔼 La Sentinelle (N > 70)**")
                st.markdown("Coût Cognitif Élevé. Nécessite des **Zones Tampons** (Pauses de sécurité).", unsafe_allow_html=True)

            with n2:
                st.markdown("**⏺️ Le Régulateur (30-70)**")
                st.markdown("Tolérance standard. Planification classique avec **Marges d'erreur**.", unsafe_allow_html=True)

            with n3:
                st.markdown("**🔽 Le Stoïque (N < 30)**")
                st.markdown("Imperméable au stress. Autorise une **Densité Maximale** de tâches.", unsafe_allow_html=True)

        
        # SECTION ANALYSE IA + CARTE RPG
        st.markdown("---")
        st.markdown("#### 🧬 Votre Neuro-Audit")

        with st.container(border=True):
            st.info(f"💡 **Stratégie Cognitive Détectée :** {data.get('analysis_global', 'Analyse en cours...')}")

            col_card, col_radar = st.columns([1.3, 1], gap="medium")
            
            with col_card:
                st.markdown(f"""
                <div class="rpg-card" style="text-align: left; background-color: #151515; border: 1px solid #333; border-radius: 10px; padding: 20px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div style="font-size:11px; color:#FF4B4B; font-weight:bold; letter-spacing:1px; text-transform:uppercase; border:1px solid #FF4B4B; padding: 2px 6px; border-radius:4px;">
                        🧬 Rareté : {data.get('rarity', 'N/A')}
                        </div>
                        <div style="font-size:11px; color:#666;">ID: #OCEAN-{random.randint(1000,9999)}</div>
                    </div>
                    <div class="archetype-title" style="text-align:left; margin-top:15px; font-size:24px; color:#fff; font-weight:bold;">
                    {data.get('archetype', 'Architecte')}
                    </div>
                    <div style="font-style:italic; color:#aaa; margin-top:5px; font-size:13px; border-left: 3px solid #555; padding-left: 10px;">
                    "{data.get('quote', 'Pas de citation')}"
                    </div>
                    <hr style="border-color:#333; margin: 20px 0; opacity:0.5;">
                    <div style="background: rgba(255, 75, 75, 0.1); padding: 12px; border-radius: 6px; border-left: 3px solid #FF4B4B; margin-bottom: 20px;">
                        <div style="color:#FF4B4B; font-weight:bold; font-size:11px; margin-bottom:5px; text-transform:uppercase;">⚠️ DIAGNOSTIC SYSTÈME :</div>
                        <div style="color:#ddd; font-size:12px; line-height:1.4;">
                        Configuration neuronale atypique détectée. Ce profil présente un potentiel de haute performance bridé par des frictions spécifiques.
                        </div>
                    </div>
                    <div style="margin-bottom: 15px;">
                        <div style="color:#888; font-size:10px; text-transform:uppercase; letter-spacing:1px; margin-bottom:3px;">
                        ⚔️ Vecteur de Puissance
                        </div>
                        <div style="color:#00ff00; font-weight:bold; font-size:15px; background: rgba(0,255,0,0.05); padding: 8px; border-radius:4px; border: 1px solid rgba(0,255,0,0.1);">
                        {data.get('superpower', 'N/A')}
                        </div>
                    </div>
                    <div>
                        <div style="color:#888; font-size:10px; text-transform:uppercase; letter-spacing:1px; margin-bottom:3px;">
                        🔴 Point de Rupture
                        </div>
                        <div style="color:#FF4B4B; font-weight:bold; font-size:15px; background: rgba(255,75,75,0.05); padding: 8px; border-radius:4px; border: 1px solid rgba(255,75,75,0.1);">
                        {data.get('kryptonite', 'N/A')}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_radar:
                # Récupération des scores sauvegardés si besoin
                if saved_scores:
                    df_scores = pd.DataFrame(dict(r=list(saved_scores.values()), theta=list(saved_scores.keys())))
                    fig = px.line_polar(df_scores, r='r', theta='theta', line_close=True, range_r=[0,100])
                    
                    fig.update_traces(fill='toself', line_color='#FF4B4B', line_width=2)
                    fig.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)", 
                        plot_bgcolor="rgba(0,0,0,0)",
                        margin=dict(l=20, r=20, t=20, b=20),
                        polar=dict(
                            radialaxis=dict(visible=True, range=[0, 100], color="#555", showticklabels=False), 
                            angularaxis=dict(color="white"),
                            bgcolor="rgba(255, 255, 255, 0.05)"
                        )
                    )
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # TABLEAU PLANNING
        st.markdown("### 🗓️ Protocole d'Exécution (Planning)")
        planning = data.get("planning", [])
        if len(planning) > 0:
            df_free = pd.DataFrame(planning)
            try:
                df_display = df_free[["start_iso", "titre", "categorie", "description"]].copy()
                df_display["Heure"] = df_display["start_iso"].apply(lambda x: x.split('T')[1][:5] if 'T' in x else x)
                df_display = df_display[["Heure", "titre", "categorie", "description"]]
                df_display.columns = ["🕒 Heure", "📝 Action", "🏷️ Catégorie", "ℹ️ Consigne Tactique"]
                st.dataframe(df_display, hide_index=True, use_container_width=True)
            except:
                st.dataframe(df_free, hide_index=True, use_container_width=True)
        else:
            st.info("Aucun planning généré pour l'instant.")

    # --- ONGLET 2 : BIO-RYTHME ---
    with res_tab2:
        st.markdown("#### ⚡ Chronobiologie & Performance (Loi de Breus)")

        # BLOC 1 : LE POSTULAT
        with st.container(border=True):
            st.markdown('<div style="color:#00ff00; font-weight:bold; margin-bottom:10px;">🕒 1. Synchronisation Circadienne</div>', unsafe_allow_html=True)
            
            c_theo, c_eq = st.columns([2, 1], gap="large")
            with c_theo:
                st.markdown("""
                **La Réalité Biologique :**
                Le temps n'est pas linéaire, il est cyclique. Votre performance cognitive est dictée par la courbe de température corporelle et la sécrétion de Cortisol.
                Lutter contre son pic naturel génère une **Friction Métabolique** (Fatigue sans travail). L'objectif est l'alignement de phase.
                """)
            with c_eq:
                st.latex(r"P(t) = C_{ortisol}(t) \times \mu_{focus}")
                st.caption("Performance = Phase Hormonale x Coefficient Focus")

        # BLOC 2 : ARCHITECTURES SOLAIRES
        with st.container(border=True):
            st.markdown('<div style="color:#FF4B4B; font-weight:bold; margin-bottom:15px;">☀️ 2. Architectures Solaires (Early Phase)</div>', unsafe_allow_html=True)
            c_lion, c_bear = st.columns(2, gap="medium")
            
            with c_lion:
                st.markdown("#### 🦁 Le Lion (Matin - 15%)")
                st.caption("Latence Nulle | Pic : 06h-11h")
                st.success("✅ Stratégie : FRONT-LOADING")
                st.markdown("""
                **Diagnostic :**
                Démarrage système immédiat. Énergie massive le matin, effondrement linéaire dès 14h.
                <div style="margin-top:10px; border-top:1px solid #444; padding-top:5px;">
                <b>🔧 Protocole :</b><br>
                1. <b>08h-12h :</b> Deep Work Analytique (Zone Sacrée).<br>
                2. <b>Post-14h :</b> Mode Maintenance (Admin/Mails).<br>
                3. <b>Interdit :</b> Tâches complexes après 17h.
                </div>
                """, unsafe_allow_html=True)
            
            with c_bear:
                st.markdown("#### 🐻 L'Ours (Standard - 55%)")
                st.caption("Cycle Solaire | Pic : 10h-14h")
                st.info("ℹ️ Stratégie : GESTION DE CRASH")
                st.markdown("""
                **Diagnostic :**
                Montée en puissance progressive. Stabilité élevée mais sujet au **Crash Post-Prandial** (14h) violent.
                <div style="margin-top:10px; border-top:1px solid #444; padding-top:5px;">
                <b>🔧 Protocole :</b><br>
                1. <b>Matin :</b> Production & Analyse.<br>
                2. <b>14h-15h30 :</b> Tâches Low-Cognitive (Réunions, Appels).<br>
                3. <b>16h :</b> Seconde fenêtre de tir (Sprint final).
                </div>
                """, unsafe_allow_html=True)

        # BLOC 3 : ARCHITECTURES ATYPIQUES
        with st.container(border=True):
            st.markdown('<div style="color:#FF4B4B; font-weight:bold; margin-bottom:15px;">🌙 3. Architectures Décalées (Late Phase)</div>', unsafe_allow_html=True)
            c_wolf, c_dolphin = st.columns(2, gap="medium")
            
            with c_wolf:
                st.markdown("#### 🐺 Le Loup (Soir - 15%)")
                st.caption("Inversion Cortisol | Pic : 17h-00h")
                st.warning("⚠️ Stratégie : DÉMARRAGE DÉFENSIF")
                st.markdown("""
                **Diagnostic :**
                Forte "Inertie du Sommeil" (Brouillard mental matinal). Pic créatif nocturne. Socialement décalé.
                <div style="margin-top:10px; border-top:1px solid #444; padding-top:5px;">
                <b>🔧 Protocole :</b><br>
                1. <b>Avant 11h :</b> Veille, Lecture (Pas de Création).<br>
                2. <b>17h-Minuit :</b> Prime Time (Bloquez ce créneau).<br>
                3. <b>Acceptation :</b> Ne luttez pas pour être "du matin".
                </div>
                """, unsafe_allow_html=True)

            with c_dolphin:
                st.markdown("#### 🐬 Le Dauphin (Chaos - 10%)")
                st.caption("Signal Bruité | Pic : Erratique")
                st.error("🚨 Stratégie : MICRO-SPRINTS")
                st.markdown("""
                **Diagnostic :**
                Sommeil fragmenté. Fonctionne à "l'énergie nerveuse". Fatigué mais alerte ("Wired but tired").
                <div style="margin-top:10px; border-top:1px solid #444; padding-top:5px;">
                <b>🔧 Protocole :</b><br>
                1. <b>Opportunisme :</b> Travaillez dès qu'une fenêtre s'ouvre.<br>
                2. <b>Sprints Courts :</b> 45min max (Pomodoro strict).<br>
                3. <b>Siestes :</b> Power naps de 20min vitales.
                </div>
                """, unsafe_allow_html=True)

        # SECTION GRAPHIQUE (Plotly)
        st.markdown("---")
        st.markdown("#### 🌊 Votre Courbe de Puissance Cognitive")
        
        st.info(f"🧬 **Analyse Personnalisée :** {data.get('analysis_bio', 'Calcul en cours...')}")
        
        energy_data = data.get("chart_energy", [])
        if energy_data:
            df_energy = pd.DataFrame(energy_data)
            fig_energy = px.line(df_energy, x="heure", y="niveau", markers=True, line_shape="spline")
            
            fig_energy.update_traces(line_color='#00ff00', line_width=4, marker_size=8, marker_color='#ffffff')
            fig_energy.add_hline(y=80, line_dash="dot", line_color="rgba(255,255,255,0.5)", annotation_text="Zone Hyperfocus")
            
            fig_energy.update_layout(
                xaxis_title="Heure de la Journée", 
                yaxis_title="Niveau d'Énergie (0-100)",
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0.2)", 
                font=dict(color="white"),
                hovermode="x unified",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
            )
            st.plotly_chart(fig_energy, use_container_width=True)
        else:
            st.warning("⚠️ Données d'énergie non disponibles.")

    # --- ONGLET 3 : MATRICE ÉNERGIE ---
    with res_tab3:
        st.markdown("#### 🧬 La Dynamique Énergétique (Cortical Arousal)")

        # BLOC 1 : LE POSTULAT
        with st.container(border=True):
            st.markdown('<div style="color:#00ff00; font-weight:bold; margin-bottom:10px;">⚡ 1. Le Bilan Métabolique (Loi de Eysenck)</div>', unsafe_allow_html=True)
            c_theo, c_eq = st.columns([2, 1], gap="large")
            with c_theo:
                st.markdown("""
                **La Réalité Neurologique :**
                L'énergie cognitive n'est pas une question de "volonté", mais de **Seuil d'Activation Cortical** (ARAS). 
                Le cerveau cherche constamment l'homéostasie (niveau de stimulation optimal).
                * Un cerveau *Introverti* est naturellement **saturé** (High Arousal) -> Il cherche à réduire le signal.
                * Un cerveau *Extraverti* est naturellement **sous-alimenté** (Low Arousal) -> Il cherche à augmenter le signal.
                """)
            with c_eq:
                st.latex(r"\Delta E = E_{stimulus} - E_{cost}")
                st.caption("Énergie Résiduelle = Stimulation Reçue - Coût Cognitif")

        # BLOC 2 : LES 3 ARCHITECTURES
        with st.container(border=True):
            st.markdown('<div style="color:#FF4B4B; font-weight:bold; margin-bottom:15px;">🧠 2. Architectures & Protocoles</div>', unsafe_allow_html=True)
            col_intro, col_ambi, col_extro = st.columns(3, gap="medium")
            
            # --- INTRO ---
            with col_intro:
                st.markdown("#### 🛡️ Interne (E < 40)")
                st.caption("Cortex Haute Fréquence")
                st.info("⚠️ Sensibilité : HAUTE")
                st.markdown("""
                **Mécanisme :**
                Cortex pré-activé. Tout stimulus externe est traité comme une **Agression Sensorielle**.
                <br>
                **L'Équation :**
                * Interaction = 🟥 DRAIN MASSIF
                * Solitude = 🟩 RECHARGE OBLIGATOIRE
                <div style="margin-top:10px; border-top:1px solid #444; padding-top:5px;">
                <b>🔧 Protocoles Impératifs :</b><br>
                1. <b>Radical Batching :</b> 0 réunion le matin.<br>
                2. <b>Buffer 15' :</b> Silence absolu après visio.<br>
                3. <b>Async First :</b> Refusez les appels non-planifiés.
                </div>
                """, unsafe_allow_html=True)

            # --- AMBI ---
            with col_ambi:
                st.markdown("#### ⚖️ Central (40-60)")
                st.caption("L'Hybride Contextuel")
                st.warning("⚠️ Risque : Crash Silencieux")
                st.markdown("""
                **Mécanisme :**
                Plasticité neuronale. Vous pouvez simuler l'extraversion, mais votre batterie a une capacité fixe.
                <br>
                **L'Équation :**
                * Interaction = 🟨 COÛT DIFFÉRÉ
                * Solitude = 🟨 MAINTENANCE CYCLIQUE
                <div style="margin-top:10px; border-top:1px solid #444; padding-top:5px;">
                <b>🔧 Protocoles Impératifs :</b><br>
                1. <b>Pendule 24h :</b> Matin Social / Aprèm Deep Work.<br>
                2. <b>Monitoring :</b> Ne jamais enchaîner 2 jours "Full Social".<br>
                3. <b>Sanctuarisation :</b> 2h/jour bloquées sans négo.
                </div>
                """, unsafe_allow_html=True)

            # --- EXTRO ---
            with col_extro:
                st.markdown("#### 📡 Externe (E > 60)")
                st.caption("Seuil d'Activation Élevé")
                st.success("✅ Besoin Stimulus : HAUT")
                st.markdown("""
                **Mécanisme :**
                Cortex hypo-actif. Le silence est interprété comme une **Menace**. Besoin de friction externe.
                <br>
                **L'Équation :**
                * Interaction = 🟩 GAIN D'ÉNERGIE
                * Isolation = 🟥 ATROPHIE
                <div style="margin-top:10px; border-top:1px solid #444; padding-top:5px;">
                <b>🔧 Protocoles Impératifs :</b><br>
                1. <b>Body Doubling :</b> Travaillez en café/co-working.<br>
                2. <b>Ping-Pong :</b> Réfléchissez en parlant.<br>
                3. <b>Mouvement :</b> Pas de station assise > 45min.
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("#### 🔋 Coût Énergétique des Tâches")
        st.info(f"🔋 **Analyse de la Batterie Interne :** {data.get('analysis_social', 'Calcul...')}")
        
        matrix_data = data.get("chart_matrix", [])
        if matrix_data:
            df_matrix = pd.DataFrame(matrix_data)
            fig_matrix = go.Figure(go.Bar(
                x=df_matrix['impact'],
                y=df_matrix['tache'],
                orientation='h',
                marker=dict(
                    color=df_matrix['impact'],
                    colorscale='RdYlGn', 
                    line=dict(color='rgba(255, 255, 255, 0.3)', width=1)
                )
            ))
            fig_matrix.update_layout(
                xaxis_title="Drain (-) vs Recharge (+)",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"), margin=dict(l=10, r=10, t=30, b=30)
            )
            st.plotly_chart(fig_matrix, use_container_width=True)
        else:
            st.warning("⚠️ Données matrice non disponibles.")

    # --- ONGLET 4 : MÉCANIQUE DE L'ACTION ---
    with res_tab4:
        st.markdown("#### ⚙️ Modèle B=MAT : Thermodynamique de l'Action")
        
        # BLOC 1 : L'ÉQUATION
        with st.container(border=True):
            st.markdown('<div style="color:#00ff00; font-weight:bold; margin-bottom:10px;">🧪 1. L\'Équation Non-Linéaire</div>', unsafe_allow_html=True)
            col_form, col_desc = st.columns([1, 2], gap="large")
            with col_form:
                st.latex(r"B = M \times A \times T")
                st.caption("Behavior = Motivation x Ability x Trigger")
                st.markdown("""
                <div style="background-color:#1c202a; padding:10px; border-radius:5px; font-size:12px; border:1px solid #333; margin-top:10px;">
                <b>Règle du Zéro :</b><br>
                L'équation est multiplicative. Si une variable est nulle, le résultat est 0.
                </div>
                """, unsafe_allow_html=True)
            with col_desc:
                st.markdown("""
                **Le Postulat de B.J. Fogg (Stanford) :**
                L'inaction n'est pas une défaillance morale, mais un échec d'architecture.
                * **Dynamique :** Tâche dure (Capacité faible) = Motivation requise très élevée. Tâche simple = Motivation faible suffit.
                * **Erreur :** Tenter de forcer la Motivation (M) alors que le levier est la Capacité (A).
                """)

        # BLOC 2 : VARIABLES
        with st.container(border=True):
            st.markdown('<div style="color:#FF4B4B; font-weight:bold; margin-bottom:15px;">🧩 2. Décomposition des Vecteurs</div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3, gap="medium")
            
            with c1:
                st.markdown("#### 🔥 M - Motivation")
                st.caption("L'Oscillateur (Dopamine)")
                st.markdown("""
                **Nature :** Ondulatoire et imprévisible. Dépend du sommeil, glucose, stress.
                <br>
                **Analyse :** Baser une routine sur la motivation est une faute systémique.
                *Stratégie :* Profiter des vagues pour les tâches dures, mais concevoir pour les jours "sans".
                """, unsafe_allow_html=True)
            
            with c2:
                st.markdown("#### 🧱 A - Capacité")
                st.caption("La Résistance (Friction)")
                st.markdown("""
                **Nature :** Le Coût Métabolique. Loi du Moindre Effort.
                <br>
                **Analyse :** Procrastination = Ratio Récompense/Coût négatif.
                *Stratégie :* Réduire la taille de la tâche jusqu'à friction zéro (Tiny Habits).
                """, unsafe_allow_html=True)
            
            with c3:
                st.markdown("#### ⚡ T - Déclencheur")
                st.caption("L'Interrupteur (Signal)")
                st.markdown("""
                **Nature :** L'Appel à l'Action. Pas de comportement sans prompt.
                <br>
                **Analyse :** Un trigger doit être "Chaud" (Actionnable immédiatement).
                *Types :* Spark (Motivation), Facilitator (Capacité), Signal (Rappel).
                """, unsafe_allow_html=True)

        # BLOC 3 : TOPOLOGIE
        with st.container(border=True):
            st.markdown('<div style="color:#aaa; font-weight:bold; margin-bottom:10px;">📍 3. Topologie de l\'Échec et de la Réussite</div>', unsafe_allow_html=True)
            z1, z2, z3 = st.columns(3, gap="medium")
            with z1:
                st.error("🔴 Zone de Procrastination")
                st.markdown("**Diagnostic : Friction > Motivation**")
                st.markdown("Le cerveau perçoit une menace énergivore. **Sortie :** Division par 10.", unsafe_allow_html=True)
            with z2:
                st.warning("⚠️ Le Piège Dopaminergique")
                st.markdown("**Diagnostic : Motivation > Friction 0**")
                st.markdown("Scroll infini, jeux. **Sortie :** Friction Artificielle (éloigner téléphone).", unsafe_allow_html=True)
            with z3:
                st.success("🟢 La Zone de Flow")
                st.markdown("**Diagnostic : Alignement M=A**")
                st.markdown("Compétence = Challenge. **Maintien :** Protéger contre les interruptions.", unsafe_allow_html=True)

        fogg_data = data.get("chart_fogg", [])
        if fogg_data:
            df_fogg = pd.DataFrame(fogg_data)
            fig_fogg = px.scatter(
                df_fogg, 
                x="friction", 
                y="dopamine", 
                text="tache",
                size="importance",
                color="zone",
                color_discrete_map={"Action": "#00ff00", "Procrastination": "#ff0000", "Piège": "#ffff00"},
                hover_data=["description"]
            )
            fig_fogg.add_shape(type="line", x0=0, y0=0, x1=100, y1=100,
                            line=dict(color="white", width=2, dash="dot"))
            fig_fogg.update_traces(textposition='top center', marker=dict(opacity=0.8, line=dict(width=1, color='DarkSlateGrey')))
            fig_fogg.update_layout(
                xaxis_title="Friction (Difficulté perçue)",
                yaxis_title="Dopamine (Récompense anticipée)",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(20,20,20,0.5)",
                font=dict(color="white"),
                showlegend=True
            )
            st.plotly_chart(fig_fogg, use_container_width=True)
            st.info(f"💡 **Protocole de Déblocage :** {data.get('analysis_fogg', 'Calcul...')}")
        else:
            st.warning("Données Fogg indisponibles.")

    # --- PAYWALL (TOUJOURS EN BAS) ---
    st.markdown('<div class="locked-section">', unsafe_allow_html=True)
    st.write("🔒 **RAPPORT NEURO-PSYCHOLOGIQUE COMPLET VERROUILLÉ**")
    
    col_blur, col_pitch = st.columns([1.5, 1])
    with col_blur:
        st.markdown("#### Analyse Croisée (OCEAN x Habitudes) :")
        # On utilise les scores sauvegardés pour éviter le crash
        conscience_val = saved_scores.get("Conscience", 50)
        st.markdown(f'<div class="blur-text">Votre Conscience ({conscience_val}%) entre en conflit avec votre habitude "{saved_tendency}". L IA a détecté un risque élevé de paralysie décisionnelle...</div>', unsafe_allow_html=True)
        st.markdown("#### Les Prompts Secrets Activés :")
        st.markdown('<div class="blur-text"><System> Override circadian rythm for Night Owl profile...</div>', unsafe_allow_html=True)

    with col_pitch:
        st.info("📦 **PACK EXPERT (9.90€)**")
        st.markdown("""
        ✅ **Planning Intégral** (.ics)
        ✅ **Analyse Neuro-Cross**
        ✅ **Les Prompts Secrets**
        """)
        st.link_button("🔓 DÉBLOQUER MAINTENANT", "https://buy.stripe.com/00w7sN5ZW5gp9GggtP0RG00", type="primary")
    
    st.markdown('</div>', unsafe_allow_html=True)