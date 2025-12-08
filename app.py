import streamlit as st
import json
import pandas as pd
import plotly.express as px
from backend import parse_schedule, generate_ics_file

st.set_page_config(page_title="Chaos Manager Pro", page_icon="🧠", layout="wide")

# --- CSS EXPERT ---
st.markdown("""
<style>
.big-font { font-size:20px !important; font-weight: bold; }
.blur-text { filter: blur(5px); user-select: none; color: #666; }
.locked-section { border: 2px dashed #ff4b4b; padding: 20px; border-radius: 10px; background-color: #fff9f9; text-align: center;}
.success-box { padding:15px; border-radius:10px; background-color:#d4edda; color:#155724; border:1px solid #c3e6cb; text-align:center;}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR (Minimaliste maintenant) ---
with st.sidebar:
    st.header("🧠 Chaos Manager V3")
    st.info("Système d'ingénierie temporelle assisté par IA.")
    st.markdown("---")
    st.write("Le diagnostic se base sur le modèle **Big Five Productivity**.")

# --- HEADER ---
st.title("🧠 Chaos Manager : Expert Edition")
st.subheader("Ne planifie pas juste ta semaine. Hacke ton cerveau.")

# --- LES 3 SONDES PSYCHIQUES ---
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 1. Autopsie de l'Échec 💀")
    input_echec = st.text_area(
        "Pense à ton dernier projet raté. Qu'est-ce qui a VRAIMENT causé l'échec ?",
        placeholder="Ex: J'ai abandonné quand c'est devenu dur (perte de sens), ou j'ai voulu faire trop parfait (perfectionnisme)...",
        height=120
    )

    st.markdown("### 2. Cartographie Énergie ⚡")
    input_energie = st.text_area(
        "Comment fonctionne ton moteur ?",
        placeholder="Ex: Je suis un sprinter (gros rush puis crash), ou j'ai besoin de deadline pour démarrer...",
        height=120
    )

with col2:
    st.markdown("### 3. La Mission 🎯")
    input_mission = st.text_area(
        "Vide ton cerveau (Liste des tâches brute) :",
        placeholder="Ex: Partiel physique vendredi, MMA mardi 19h, rendre projet Python dimanche, acheter pain...",
        height=320
    )

# --- ACTION ---
if st.button("🚀 LANCER LE DIAGNOSTIC & GÉNÉRER", type="primary", use_container_width=True):
    if not input_mission:
        st.warning("Il me faut au moins une mission (Zone 3) !")
    else:
        with st.spinner("Analyse cognitive en cours... Calcul des scores Big Five..."):
            try:
                # Packaging
                inputs = {
                    "echec": input_echec,
                    "energie": input_energie,
                    "mission": input_mission
                }
                
                # APPEL BACKEND
                raw_resp = parse_schedule(inputs)
                data = json.loads(raw_resp)
                
                # --- DÉTECTEUR D'ERREUR ---
                if "error" in data:
                    st.error(f"🚨 ERREUR DU CERVEAU : {data['error']}")
                    st.stop() # On arrête tout ici si ça plante
                
                # --- RÉSULTATS (Si tout va bien) ---
                
                # 1. ARCHÉTYPE & RADAR (L'Effet Wow)
                st.markdown("---")
                col_res1, col_res2 = st.columns([1, 1])
                
                with col_res1:
                    st.markdown(f"<div class='success-box'><h2>👤 {data.get('archetype', 'Inconnu')}</h2></div>", unsafe_allow_html=True)
                    st.caption("Archétype calculé selon tes réponses.")
                    
                    # Graphique Radar avec Plotly
                    scores = data.get("scores", {"Focus": 50, "Discipline": 50})
                    df_scores = pd.DataFrame(dict(
                        r=list(scores.values()),
                        theta=list(scores.keys())
                    ))
                    fig = px.line_polar(df_scores, r='r', theta='theta', line_close=True, range_r=[0,100])
                    fig.update_traces(fill='toself', line_color='#FF4B4B')
                    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig, use_container_width=True)

                with col_res2:
                    # 2. LE PLANNING (Preuve)
                    st.subheader("📅 Ton Planning Stratégique")
                    planning = data.get("planning", [])
                    if planning:
                        df = pd.DataFrame(planning)
                        st.dataframe(df[["titre", "start_iso", "end_iso", "categorie"]], hide_index=True, use_container_width=True)

                # --- LE PÉAGE (L'EXPERTISE) ---
                st.markdown("---")
                col_lock, col_buy = st.columns([2, 1])
                
                with col_lock:
                    st.markdown('<div class="locked-section">', unsafe_allow_html=True)
                    st.warning("🔒 **DIAGNOSTIC CLINIQUE VERROUILLÉ**")
                    st.markdown("### Ce que l'IA a découvert sur toi :")
                    
                    # Teaser dynamique
                    st.write(f"**Diagnostic :** {data.get('diagnosis', '')[:50]}...")
                    st.markdown('<p class="blur-text">Le sujet démontre une forte capacité d impulsion mais un score de structure critique (30/100). Cela explique les échecs récents. La stratégie adoptée est le Time-Boxing inversé pour...</p>', unsafe_allow_html=True)
                    
                    st.write("**Le Hack Cognitif appliqué :**")
                    st.markdown('<p class="blur-text">Pour contrer ton profil Sprinter, j ai segmenté les tâches en blocs de 45min avec interdiction de pause...</p>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                with col_buy:
                    st.info("📦 **PACK EXPERT**")
                    st.markdown("""
                    - 📊 **Ton Bilan Psychométrique complet**
                    - 🧠 **Le Mode d'emploi de ton cerveau**
                    - 📥 **Export Agenda (.ics)**
                    """)
                    
                    # --- TON LIEN STRIPE LIVE ICI ---
                    st.link_button(
                        "🔓 DÉBLOQUER L'EXPERTISE (9.90€)", 
                        "https://buy.stripe.com/00w7sN5ZW5gp9GggtP0RG00"
                    )
                    st.caption("Investis en toi-même.")

            except Exception as e:
                st.error(f"Erreur système : {e}")