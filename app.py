import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go # Pour les graphiques avancés
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
# --- FORMULAIRE ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("#### 1. Calibration Neuro-Psychologique")
st.caption("Remplis ces jauges. L'IA va sélectionner les 'Secret Prompts' adaptés à tes scores.")


with st.form("psycho_form"):
    with st.expander("📖 Théorie : Comment l'IA structure votre temps (Modèle OCEAN)"):
            st.markdown("""
            **Le principe : L'Isomorphisme Cognitif**
            Un agenda n'est efficace que s'il imite la structure naturelle de vos pensées. Nous utilisons principalement deux vecteurs pour sculpter le temps :
            
            1.  **L'Axe de la Conscience (C) : La Rigidité Structurelle**
                * **Si C > 75 (L'Architecte) :** Votre cerveau a besoin de prévisibilité. L'IA génère des blocs longs (90min), séquentiels et immuables. L'échec vient souvent d'un manque de planification.
                * **Si C < 30 (Le Chaos Pilot) :** Votre cerveau fonctionne par "sauts" d'intérêt. L'IA fragmente le temps en *Sprints* (25-45min) et varie les types de tâches pour maintenir la dopamine. L'échec vient de l'ennui et de la routine.
            
            2.  **L'Axe du Névrosisme (N) : La Gestion de la Charge**
                * **Si N > 70 (Sentinelle) :** Le stress vous coûte cher en énergie. L'IA insère des "Zones Tampon" (Buffer) de 15min entre les tâches pour éviter la surchauffe cognitive.
                * **Si N < 30 (Stoïque) :** Vous tolérez la pression. L'IA peut "tasser" les tâches (Time-Blocking dense) pour maximiser le rendement pur.
            """)
    # === ONGLETS OCEAN ===
    tab1, tab2 = st.tabs(["📂 J'ai déjà mes scores (Expert)", "🔍 Je ne sais pas (Estimation)"])
    
    # --- ONGLET 1 : SAISIE EXPERTE (Numérique + Explication) ---
    with tab1:
        st.markdown("""
        <div style="background-color: #1c202a; padding: 15px; border-radius: 8px; margin-bottom: 25px; border: 1px solid #00ff00;">
            ✅ <b>Mode Expert :</b> Entrez vos scores (0-100).
            L'IA détectera votre polarité dominante pour calibrer les instructions cachées.
        </div>
        """, unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("##### 🧠 Le Cerveau (Traitement de l'Info)")
            
            # OUVERTURE
            o_score = st.number_input("🌊 Ouverture (O) - Créativité", 0, 100, 0, key="o_in")
            st.markdown("""
            <div style="font-size:12px; color:#aaa; margin-bottom:15px; border-left:2px solid #555; padding-left:10px;">
                <b>⬆️ Haut (>75 - Visionnaire) :</b> Besoin de variété et d'innovation.<br>
                <b>⬇️ Bas (<25 - Pragmatique) :</b> Besoin de processus et d'efficacité prouvée.
            </div>
            """, unsafe_allow_html=True)
            
            # CONSCIENCE
            c_score = st.number_input("📐 Conscience (C) - Organisation", 0, 100, 0, key="c_in")
            st.markdown("""
            <div style="font-size:12px; color:#aaa; margin-bottom:15px; border-left:2px solid #555; padding-left:10px;">
                <b>⬆️ Haut (>75 - Architecte) :</b> Besoin de plans détaillés à l'avance.<br>
                <b>⬇️ Bas (<25 - Pompier) :</b> Besoin d'urgence et de deadlines courtes pour s'activer.
            </div>
            """, unsafe_allow_html=True)

            # EXTRAVERSION
            e_score = st.number_input("⚡ Extraversion (E) - Énergie Sociale", 0, 100, 0, key="e_in")
            st.markdown("""
            <div style="font-size:12px; color:#aaa; margin-bottom:15px; border-left:2px solid #555; padding-left:10px;">
                <b>⬆️ Haut (>75 - Connecteur) :</b> L'isolement vous vide, le groupe vous recharge.<br>
                <b>⬇️ Bas (<25 - Deep Worker) :</b> Le groupe vous vide, le silence vous recharge.
            </div>
            """, unsafe_allow_html=True)
        
        with col_b:
            st.markdown("##### ❤️ Le Coeur (Gestion Émotionnelle)")
            
            # AGRÉABILITÉ
            a_score = st.number_input("🤝 Agréabilité (A) - Coopération", 0, 100, 0, key="a_in")
            st.markdown("""
            <div style="font-size:12px; color:#aaa; margin-bottom:15px; border-left:2px solid #555; padding-left:10px;">
                <b>⬆️ Haut (>75 - Diplomate) :</b> Priorité à l'équipe (Risque : ne sait pas dire non).<br>
                <b>⬇️ Bas (<25 - Stratège) :</b> Priorité à l'objectif (Force : négociation ferme).
            </div>
            """, unsafe_allow_html=True)
            
            # NÉVROSISME
            n_score = st.number_input("🌪️ Névrosisme (N) - Sensibilité Stress", 0, 100, 0, key="n_in")
            st.markdown("""
            <div style="font-size:12px; color:#aaa; margin-bottom:15px; border-left:2px solid #555; padding-left:10px;">
                <b>⬆️ Haut (>75 - Sentinelle) :</b> Hyper-vigilance aux risques (Besoin de rassurance).<br>
                <b>⬇️ Bas (<25 - Stoïque) :</b> Imperméabilité au stress (Force calme).
            </div>
            """, unsafe_allow_html=True)

    # --- ONGLET 2 : SLIDERS (Estimation) ---
    with tab2:
        st.markdown("""
        <div style="background-color: #262730; padding: 15px; border-radius: 8px; margin-bottom: 20px; font-size: 14px; border: 1px solid #444;">
            ℹ️ <b>Calibration Cognitive :</b> Positionnez le curseur selon votre tendance naturelle au travail. 
            Il n'y a pas de "bon" score. Un score bas en Conscience favorise la créativité, un score haut favorise l'exécution.
        </div>
        """, unsafe_allow_html=True)

        # O
        st.markdown("#### 🌊 1. Facteur O : La Nouveauté (Ouverture)")
        st.caption("🧠 *Impact Travail : Capacité à tolérer la routine vs Besoin d'innovation.*")
        st.markdown("""**0% (Pragmatique)** : J'aime les processus clairs, la répétition, l'efficacité éprouvée.<br>**100% (Explorateur)** : Je m'ennuie vite, j'ai besoin de théoriser et de changer de méthode souvent.""", unsafe_allow_html=True)
        o_est = st.slider("Votre positionnement O :", 0, 100, 50, key="slider_o", label_visibility="collapsed")
        st.markdown("---")

        # C
        st.markdown("#### 📐 2. Facteur C : La Structure (Conscience)")
        st.caption("🧠 *Impact Travail : Gestion des délais et finition des tâches.*")
        st.markdown("""**0% (Spontané)** : Je travaille par "bursts" d'énergie, je suis flexible mais désordonné. Je démarre beaucoup de choses.<br>**100% (Architecte)** : Je planifie tout à l'avance, je finis toujours ce que je commence, je suis mal à l'aise sans plan.""", unsafe_allow_html=True)
        c_est = st.slider("Votre positionnement C :", 0, 100, 50, key="slider_c", label_visibility="collapsed")
        st.markdown("---")

        # E
        st.markdown("#### ⚡ 3. Facteur E : La Stimulation (Extraversion)")
        st.caption("🧠 *Impact Travail : Gestion de l'environnement et des réunions.*")
        st.markdown("""**0% (Deep Worker)** : Les interactions me drainent. Je suis ultra-efficace seul dans le silence.<br>**100% (Connecteur)** : Je pense en parlant. L'isolement m'épuise, j'ai besoin du buzz de l'équipe pour avancer.""", unsafe_allow_html=True)
        e_est = st.slider("Votre positionnement E :", 0, 100, 50, key="slider_e", label_visibility="collapsed")
        st.markdown("---")

        # A
        st.markdown("#### 🤝 4. Facteur A : La Coopération (Agréabilité)")
        st.caption("🧠 *Impact Travail : Négociation et capacité à dire Non.*")
        st.markdown("""**0% (Challenger)** : Je priorise mes objectifs, je sais dire non fermement, quitte à être perçu comme froid.<br>**100% (Diplomate)** : Je cherche l'harmonie, j'ai du mal à refuser une demande d'aide, je fais passer l'équipe avant moi.""", unsafe_allow_html=True)
        a_est = st.slider("Votre positionnement A :", 0, 100, 50, key="slider_a", label_visibility="collapsed")
        st.markdown("---")

        # N
        st.markdown("#### 🌪️ 5. Facteur N : La Réactivité (Névrosisme)")
        st.caption("🧠 *Impact Travail : Gestion du stress et perfectionnisme.*")
        st.markdown("""**0% (Roc)** : Le stress glisse sur moi. Je reste calme en crise, parfois détaché.<br>**100% (Sentinelle)** : Je suis hyper-vigilant aux risques. Je repère les erreurs, mais le stress me paralyse ou me rend perfectionniste.""", unsafe_allow_html=True)
        n_est = st.slider("Votre positionnement N :", 0, 100, 50, key="slider_n", label_visibility="collapsed")

    # --- SECTION SOFTWARE (Breus, Rubin, Lencioni) ---
    st.markdown("---")
    st.write("#### 2. Calibration du 'Software' (Mécanique de Travail)")
    st.caption("Ici, on analyse vos habitudes selon 3 modèles de productivité reconnus.")

    # MODEL 1: CHRONOTYPES
    st.markdown("""
    <div style="margin-top:20px; border-left:3px solid #FF4B4B; padding-left:15px;">
        <h5>🦁 Le Rythme Biologique (Modèle du Dr. Michael Breus)</h5>
        <small>Votre horloge interne dicte vos pics de cortisol.</small>
    </div>
    """, unsafe_allow_html=True)

    col_chrono_desc, col_chrono_sel = st.columns([1.5, 1])
    with col_chrono_desc:
        st.markdown("""
        * **🦁 Le Lion (Matin) :** Réveil naturel tôt. Épuisé à 21h. *Stratégie : Tâches analytiques dès 8h.*
        * **🐻 L'Ours (Solaire) :** Suit le soleil. Pic de 10h à 14h. *Stratégie : Planning classique équilibré.*
        * **🐺 Le Loup (Soir) :** Pic créatif à 19h ou minuit. *Stratégie : Pas de tâches lourdes avant 11h.*
        * **🐬 Le Dauphin (Irrégulier) :** Sommeil léger, anxieux. *Stratégie : Sprints courts et flexibles.*
        """)
    with col_chrono_sel:
        chronotype = st.radio("Quel animal êtes-vous ?", ["🦁 Lion", "🐻 Ours", "🐺 Loup", "🐬 Dauphin"], label_visibility="collapsed")

    # MODEL 2: FOUR TENDENCIES
    st.markdown("---")
    st.markdown("""
    <div style="border-left:3px solid #FF4B4B; padding-left:15px;">
        <h5>⚡ La Discipline (Modèle des "4 Tendencies" de Gretchen Rubin)</h5>
        <small>Comment réagissez-vous aux attentes ?</small>
    </div>
    """, unsafe_allow_html=True)

    col_rubin_desc, col_rubin_sel = st.columns([1.5, 1])
    with col_rubin_desc:
        st.markdown("""
        * **🫡 Upholder (Le Discipliné) :** Respecte les règles. *Besoin : Un plan clair.*
        * **🤔 Questioner (Le Sceptique) :** Ne respecte que la logique. *Besoin : Des justifications.*
        * **🙏 Obliger (Le Dévoué) :** Fait tout pour les autres. *Besoin : Responsabilité externe.*
        * **🧨 Rebel (Le Rebelle) :** Résiste à toute contrainte. *Besoin : Choix et liberté.*
        """)
    with col_rubin_sel:
        tendency = st.radio("Votre tendance dominante :", ["🫡 Upholder", "🤔 Questioner", "🙏 Obliger", "🧨 Rebel"], label_visibility="collapsed")

    # MODEL 3: WORKING GENIUS
    st.markdown("---")
    st.markdown("""
    <div style="border-left:3px solid #FF4B4B; padding-left:15px;">
        <h5>⚙️ Le Moteur d'Action (Inspiré du "Working Genius" de P. Lencioni)</h5>
        <small>Quelle étape du travail vous donne de l'énergie ?</small>
    </div>
    """, unsafe_allow_html=True)

    col_len_desc, col_len_sel = st.columns([1.5, 1])
    with col_len_desc:
        st.markdown("""
        * **✨ Wonder/Invention (L'Idéateur) :** J'aime inventer. Je déteste finir.
        * **🔥 Galvanizing (L'Activateur) :** J'aime lancer la machine, organiser le chaos.
        * **🏗️ Tenacity (Le Finisseur) :** J'aime l'exécution, cocher les cases.
        """)
    with col_len_sel:
        work_genius = st.radio("Votre zone de génie :", ["✨ Idéateur (Début)", "🔥 Activateur (Milieu)", "🏗️ Finisseur (Fin)"], label_visibility="collapsed")
# --- SECTION CONTEXTE (Routine & Blocages) ---
    st.markdown("---")
    st.write("#### 3. Le Contexte & La Mission")
    
    col_input_1, col_input_2 = st.columns(2)
    
    with col_input_1:
        routine = st.text_area(
            "🔄 Ta Routine Actuelle (Habitudes)", 
            placeholder="Ex: Lever 7h, Café, Scroll TikTok 1h, Boulot, Sport le soir...", 
            height=120,
            help="Décris ta journée type actuelle pour que l'IA identifie les points de friction."
        )
        
    with col_input_2:
        blockers = st.text_area(
            "🚧 Analyse de l'Échec (Introspection)", 
            placeholder="Sois honnête. Ex: 'Je procrastine par peur de mal faire', 'Je suis distrait par les notifs', 'Je commence tout sans rien finir'...", 
            height=120,
            help="Question Clé : Qu'est-ce qui t'a empêché de réussir sur ton dernier projet ?"
        )

    # La Mission (Objectifs du jour)
    mission = st.text_area(
        "🎯 Tes Impératifs pour ce Planning", 
        placeholder="Ex: Rendre projet Python avant 18h, Appeler Maman, Séance de sport (Jambes)...", 
        height=80
    )
    
    submitted = st.form_submit_button("🚀 LANCER L'ANALYSE NEURO-CROSS", type="primary", use_container_width=True)
    

# --- LOGIQUE DE TRAITEMENT ---
if submitted:
    # Logique OCEAN intelligente
    if o_score + c_score + e_score > 0:
        final_scores = {"Ouverture": o_score, "Conscience": c_score, "Extraversion": e_score, "Agréabilité": a_score, "Névrosisme": n_score}
    else:
        final_scores = {"Ouverture": o_est, "Conscience": c_est, "Extraversion": e_est, "Agréabilité": a_est, "Névrosisme": n_est}

    # VERIFICATION : On demande au moins une mission OU un blocage pour lancer
    if not mission and not blockers:
        st.warning("Donne-moi au moins une mission ou un blocage à analyser !")
    else:
        with st.spinner("Croisement des vecteurs OCEAN x Rubin x Breus..."):
            
            # MISE A JOUR ICI : On ajoute 'routine' et 'blockers'
            inputs = {
                "scores": final_scores,
                "work_style": {
                    "chronotype": chronotype,
                    "tendency": tendency,
                    "genius": work_genius
                },
                "context": {
                    "mission": mission,
                    "routine": routine,   # <--- Nouveau
                    "blockers": blockers  # <--- Nouveau
                }
            }
            
            # Appel Backend
            data = json.loads(parse_schedule(inputs))
            # --- RÉSULTATS ---
            # --- DÉBUT DE LA GREFFE V7 (INTERFACE ONGLETS) ---
            st.markdown("---")
            
            # Création des 3 onglets de visualisation
            res_tab1, res_tab2, res_tab3 = st.tabs(["📅 Synthèse & Planning", "⚡ Bio-Rythme (New)", "🧬 Matrice Énergie (New)"])
            
            
            # --- ONGLET 1 : L'AFFICHAGE CLASSIQUE ---
            with res_tab1:
                # ZONE THEORIE (Directement visible, sans expander)
                st.markdown("""
                #### 📖 Théorie Avancée : L'Algorithme de Structuration Temporelle
                
                **Le Postulat : La Friction Cognitive**
                L'échec d'un planning ne vient pas d'un manque de volonté, mais d'une incompatibilité entre la structure du temps (l'agenda) et la structure de la pensée (le cerveau).
                
                ---
                
                ### 1. L'Axe de la Structure (Conscience)
                *Comment votre cerveau gère l'entropie et l'effort dans la durée.*
                
                * **🔼 Si C > 75 (L'Architecte / Le Séquentiel) :**
                    * *Fonctionnement :* Votre performance repose sur la continuité. Vous détestez le changement de contexte ("Task Switching"). Une interruption de 2 min peut vous coûter 20 min de reconcentration.
                    * *Stratégie IA :* **Deep Work Séquentiel.** Le planning crée des blocs massifs (90-120 min) et sanctuarisés. L'objectif est la fluidité linéaire.
                
                * **🔽 Si C < 30 (Le Chaos Pilot / Le Divergent) :**
                    * *Fonctionnement :* Votre cerveau est un moteur à combustion rapide. Il fonctionne à la "Nouveauté" et à l'Urgence. La routine linéaire génère de l'ennui, qui se transforme immédiatement en procrastination.
                    * *Stratégie IA :* **Gamification & Sprints.** Le temps est fragmenté en sessions courtes (25-45 min). On alterne les types de tâches (Créatif -> Admin -> Créatif) pour "tromper" le cerveau et maintenir le niveau de dopamine.
                    
                * **⏺️ Si C entre 30 et 75 (Le Flex-Master) :**
                    * *Stratégie IA :* **Hybridation.** Une base structurée pour le matin (pour assurer l'avancement), mais des plages de "chaos contrôlé" l'après-midi pour laisser place à l'improvisation.

                ---

                ### 2. L'Axe de la Charge Mentale (Névrosisme)
                *Le coût métabolique de l'incertitude et du risque.*

                * **🔼 Si N > 70 (La Sentinelle / Hyper-Réactif) :**
                    * *Fonctionnement :* Votre système de détection des menaces est très sensible. Un retard ou un imprévu déclenche une réponse cortisol (stress) disproportionnée qui paralyse l'action.
                    * *Stratégie IA :* **Sécurité & Tampons.** L'algorithme insère des "Airbags Temporels" (buffers de 15-20 min) entre les tâches. On évite la surcharge cognitive en ne montrant que la prochaine étape immédiate.
                
                * **🔽 Si N < 30 (Le Stoïque / Le Roc) :**
                    * *Fonctionnement :* Vous avez une haute tolérance à la pression. Les deadlines serrées agissent comme un stimulant plutôt qu'un frein. Vous récupérez vite d'un échec.
                    * *Stratégie IA :* **Densité Maximale.** Le planning est compacté ("Time-Boxing" agressif). On supprime les marges de sécurité pour maximiser le rendement pur (Yield).
                    
                * **⏺️ Si N entre 30 et 70 (Le Régulateur) :**
                    * *Stratégie IA :* **Standard.** Gestion classique des pauses (5-10 min toutes les heures) pour maintenir une homéostasie mentale stable sur la journée.
                """)
                
                # Le st.info est aligné exactement comme le st.markdown au-dessus
                st.info(f"💡 **Stratégie Cognitive :** {data.get('analysis_global', 'Analyse en cours...')}")
                
                col_card, col_radar = st.columns([1, 1])
                
                with col_card:
                    st.markdown(f"""
                    <div class="rpg-card">
                        <div style="font-size:12px; color:#FF4B4B; font-weight:bold;">🧬 PROFIL : {data.get('rarity', 'Inconnu')}</div>
                        <div class="archetype-title">{data.get('archetype', 'Architecte')}</div>
                        <p style="font-style:italic; color:#aaa; margin-top:10px;">"{data.get('quote', 'Pas de citation')}"</p>
                        <hr style="border-color:#444;">
                        <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                            <span>⚔️ Levier :</span><span style="color:white; font-weight:bold;">{data.get('superpower', 'N/A')}</span>
                        </div>
                        <div style="display:flex; justify-content:space-between;">
                            <span>⚠️ Rupture :</span><span style="color:white; font-weight:bold;">{data.get('kryptonite', 'N/A')}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with col_radar:
                    df_scores = pd.DataFrame(dict(r=list(final_scores.values()), theta=list(final_scores.keys())))
                    fig = px.line_polar(df_scores, r='r', theta='theta', line_close=True, range_r=[0,100])
                    fig.update_traces(fill='toself', line_color='#FF4B4B')
                    fig.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)", 
                        plot_bgcolor="rgba(0,0,0,0)", 
                        font=dict(color="white", size=10), 
                        margin=dict(l=40, r=40, t=30, b=30),
                        polar=dict(radialaxis=dict(visible=True, range=[0, 100], color="#555"), angularaxis=dict(color="white"))
                    )
                    st.plotly_chart(fig, use_container_width=True)

                st.subheader("📅 Aperçu Stratégique")
                planning = data.get("planning", [])
                if len(planning) > 0:
                    df_free = pd.DataFrame(planning)
                    cols_to_show = [c for c in ["titre", "start_iso", "categorie"] if c in df_free.columns]
                    st.dataframe(df_free[cols_to_show], hide_index=True, use_container_width=True)
                else:
                    st.info("Aucun planning généré pour l'instant.")
            # --- ONGLET 2 : LE BIO-RYTHME ---
            with res_tab2:
                # ZONE THEORIE (Visible directement)
                st.markdown("""
            ### 📖 Théorie : La Chronobiologie (Loi de Breus)
            **Le Postulat : L'Alignement Circadien**
            Le temps est une mesure linéaire, mais l'énergie biologique est cyclique. Votre performance dépend de votre taux de Cortisol (hormone d'éveil). Lutter contre ce pic naturel génère une friction métabolique inutile.
            
            ---

            #### 1. Les Architectures Matinales (Le Réveil Rapide)
            *Comment votre corps gère le démarrage système.*

            * 🦁 **Le Lion (Matin - 15%) :**
                * *Fonctionnement :* Latence nulle au réveil. Vous êtes opérationnel dès que les yeux s'ouvrent. Votre énergie est massive le matin mais s'effondre linéairement en fin de journée.
                * *Stratégie IA :* **Front-Loading Agressif.** 80% de votre charge cognitive (Deep Work) doit être exécutée avant 12h00. L'après-midi (après 14h) est une zone de maintenance (tâches passives, admin). Tenter de "forcer" le soir est contre-productif.

            * 🐻 **L'Ours (Solaire - 55%) :**
                * *Fonctionnement :* Vous êtes couplé au cycle solaire. Votre montée en puissance est progressive (pic vers 10h-11h). Vous possédez une stabilité élevée, mais subissez un "Crash Post-Prandial" inévitable (le coup de barre de 14h).
                * *Stratégie IA :* **Séquençage Classique.** Matin pour l'analyse et la production. Début d'après-midi (14h-15h30) pour les réunions ou tâches à faible valeur ajoutée. Reprise modérée vers 16h. Ne luttez jamais contre le creux de 14h.

            ---

            #### 2. Les Architectures Décalées (La Latence Élevée)
            *Comment votre corps gère l'inertie et la volatilité.*

            * 🐺 **Le Loup (Soir - 15%) :**
                * *Fonctionnement :* Votre pic de cortisol est inversé (vers 19h). Le matin, vous subissez une forte "inertie du sommeil" (brouillard mental). Vous êtes socialement décalé, mais créativement supérieur quand le monde dort.
                * *Stratégie IA :* **Démarrage Défensif & Attaque Nocturne.** Ne planifiez aucune tâche analytique complexe avant 11h00 (faites de la veille, lecture). Votre "Prime Time" est de 17h00 à minuit. C'est là qu'il faut isoler vos blocs de concentration.

            * 🐬 **Le Dauphin (Irrégulier - 10%) :**
                * *Fonctionnement :* Votre signal de sommeil est bruité (insomnies, réveils fréquents). Vous fonctionnez souvent à "l'énergie nerveuse" (cortisol erratique). Vous êtes souvent fatigué mais incapable de dormir ("wired but tired").
                * *Stratégie IA :* **Opportunisme & Micro-Sprints.** La planification rigide échoue avec vous. N'essayez pas de faire des blocs de 4h. Travaillez par itérations courtes (45 min) dès qu'une fenêtre de lucidité s'ouvre, quelle que soit l'heure.
            """)
                st.markdown("#### 🌊 Courbe d'Énergie Circadienne")
                st.info(f"🧬 **Analyse Chronobiologique :** {data.get('analysis_bio', 'Calcul...')}")
                
                energy_data = data.get("chart_energy", [])
                if energy_data:
                    df_energy = pd.DataFrame(energy_data)
                    fig_energy = px.line(df_energy, x="heure", y="niveau", markers=True, line_shape="spline")
                    fig_energy.update_traces(line_color='#00ff00', line_width=3)
                    fig_energy.add_hline(y=80, line_dash="dot", line_color="white", annotation_text="Zone Hyperfocus")
                    fig_energy.update_layout(
                        xaxis_title="Heure (06h - 23h)", yaxis_title="Énergie Cognitive",
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#161924", font=dict(color="white")
                    )
                    st.plotly_chart(fig_energy, use_container_width=True)
                else:
                    st.warning("⚠️ Données d'énergie non disponibles.")
            # --- ONGLET 3 : LA MATRICE ---
            with res_tab3:
                # ZONE THEORIE (Visible directement)
                st.markdown("""
            ### 📖 Théorie : La Dynamique Énergétique (Extraversion)
            **Le Postulat : Le Bilan Métabolique**
            L'énergie n'est pas seulement une question de sommeil ou de glucose. C'est une question de stimulation neurologique. Chaque type de tâche possède un "Coût Unitaire" différent selon votre câblage dopaminergique.
            
            ---

            #### 1. L'Architecture Interne (Introversion | E < 40)
            *Le cerveau à haute fréquence basale.*

            * **Fonctionnement :**
                * Votre cortex est naturellement très actif. Vous êtes sensible à la dopamine : un excès de stimulation externe (bruit, monde, notifications) provoque une surcharge sensorielle rapide.
                * **L'équation :** Interaction Sociale = 🟥 DRAIN (Coût élevé). Solitude = 🟩 RECHARGE (Maintenance).
            
            * **Stratégie IA :**
                * **Batching des Interactions :** Ne dispersez pas vos réunions. Groupez-les toutes sur une demi-journée pour limiter le coût de "changement de mode".
                * **Buffer de Décompression :** Après une réunion de 1h, insérez impérativement 15 min de solitude totale (pas de slack, pas d'email) pour vidanger le tampon cognitif.
                * **Mode Moine :** Privilégiez la communication asynchrone (écrit) pour contrôler le flux d'entrée.

            ---

            #### 2. L'Architecture Externe (Extraversion | E > 60)
            *Le cerveau à seuil d'activation élevé.*

            * **Fonctionnement :**
                * Votre niveau d'éveil naturel est bas. Pour "allumer" le système, vous avez besoin de stimulation externe. Le silence et l'immobilité prolongés sont perçus par votre cerveau comme une sous-stimulation stressante (ennui mortel).
                * **L'équation :** Interaction Sociale = 🟩 RECHARGE (Gain). Solitude Prolongée = 🟥 DRAIN (Coût).
            
            * **Stratégie IA :**
                * **Body Doubling :** Pour les tâches ennuyeuses ou difficiles, ne travaillez pas seul. Avoir quelqu'un à côté (même silencieux) ou travailler dans un café maintient votre vigilance.
                * **Ping-Pong Cognitif :** Utilisez les réunions non pas pour "rendre compte", mais pour "réfléchir à voix haute". Votre pensée se structure en s'exprimant.
                * **Pauses Actives :** Vos pauses doivent être sociales ou cinétiques, pas passives.

            ---

            #### 3. Le Spectre Central (Ambiversion | 40 < E < 60)
            *L'hybride contextuel.*

            * **Fonctionnement :**
                * Vous possédez un "interrupteur". Vous pouvez performer socialement sans coût immédiat, mais votre batterie a une capacité limitée. Le danger est l'épuisement silencieux : vous ne sentez la fatigue qu'une fois la limite franchie.
            
            * **Stratégie IA :**
                * **L'Alternance Pendulaire :** Une matinée de collaboration intense doit obligatoirement être suivie d'une après-midi de travail profond en solo. L'équilibre doit se faire sur la journée (échelle 24h), pas sur la semaine.
            """)
                
                
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
            
            # (Ici tu laisses ton Paywall 'locked-section' qui était déjà en bas)
            # --- PAYWALL ---
            st.markdown('<div class="locked-section">', unsafe_allow_html=True)
            st.write("🔒 **RAPPORT NEURO-PSYCHOLOGIQUE COMPLET VERROUILLÉ**")
            
            col_blur, col_pitch = st.columns([1.5, 1])
            with col_blur:
                st.markdown("#### Analyse Croisée (OCEAN x Habitudes) :")
                st.markdown(f'<div class="blur-text">Votre Conscience ({final_scores["Conscience"]}%) entre en conflit avec votre habitude "{tendency}". L IA a détecté un risque élevé de paralysie décisionnelle...</div>', unsafe_allow_html=True)
                st.markdown("#### Les Prompts Secrets Activés :")
                st.markdown('<div class="blur-text"><System> Override circadian rythm for Night Owl profile...</div>', unsafe_allow_html=True)

            with col_pitch:
                st.info("📦 **PACK EXPERT (9.90€)**")
                st.markdown("""
                ✅ **Planning Intégral** (.ics)
                ✅ **Analyse Neuro-Cross**
                ✅ **Les Prompts Secrets**
                """)
                # LIEN STRIPE LIVE
                st.link_button("🔓 DÉBLOQUER MAINTENANT", "https://buy.stripe.com/00w7sN5ZW5gp9GggtP0RG00", type="primary")
            
            st.markdown('</div>', unsafe_allow_html=True)