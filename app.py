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

    st.markdown("---")
    st.write("#### 3. La Mission")
    mission = st.text_area("Vos impératifs (Vrac accepté) :", placeholder="Ex: Rendre projet Python, Sport ce soir, Appeler Maman...", height=100)
    
    submitted = st.form_submit_button("🚀 LANCER L'ANALYSE NEURO-CROSS", type="primary", use_container_width=True)

# --- LOGIQUE DE TRAITEMENT ---
if submitted:
    # Logique OCEAN intelligente
    if o_score + c_score + e_score > 0:
        final_scores = {"Ouverture": o_score, "Conscience": c_score, "Extraversion": e_score, "Agréabilité": a_score, "Névrosisme": n_score}
    else:
        final_scores = {"Ouverture": o_est, "Conscience": c_est, "Extraversion": e_est, "Agréabilité": a_est, "Névrosisme": n_est}

    if not mission:
        st.warning("Donne-moi au moins une tâche !")
    else:
        with st.spinner("Croisement des vecteurs OCEAN x Rubin x Breus..."):
            
            inputs = {
                "scores": final_scores,
                "work_style": {
                    "chronotype": chronotype,
                    "tendency": tendency,
                    "genius": work_genius
                },
                "mission": mission
            }
            
            # Appel Backend
            data = json.loads(parse_schedule(inputs))
            
            # --- RÉSULTATS ---
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