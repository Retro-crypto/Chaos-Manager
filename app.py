import streamlit as st
import json
import pandas as pd
from backend import parse_schedule, generate_ics_file

st.set_page_config(page_title="Chaos Manager", page_icon="⚡", layout="wide")

# --- CSS MAGIQUE (Effet Flou + Style Archétype) ---
st.markdown("""
<style>
.blur-text {
    filter: blur(4px);
    user-select: none;
    color: #333;
    opacity: 0.7;
}
.archetype-box {
    background-color: #d4edda;
    color: #155724;
    padding: 20px;
    border-radius: 10px;
    border: 1px solid #c3e6cb;
    text-align: center;
    margin-bottom: 20px;
}
.locked-section {
    border: 2px dashed #ff4b4b;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    background-color: #fff5f5;
}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR : LE DIAGNOSTIC ---
with st.sidebar:
    st.header("🧬 Ton ADN Productif")
    st.write("Réponds honnêtement. L'IA adapte la stratégie à ta psychologie.")
    
    st.subheader("1. Ton Ennemi 👿")
    pain = st.radio(
        "Qu'est-ce qui te bloque le plus ?",
        [
            "🤯 Paralysie (Trop de choix, je bug)",
            "🛑 Procrastination (Peur de mal faire)",
            "🦋 Papillonnage (Je finis rien)",
            "🔋 Fatigue (Plus de jus après 14h)",
            "⏰ Urgence (Je ne bosse que sous pression)"
        ]
    )
    
    st.subheader("2. Ton Rythme ⚡")
    rhythm = st.select_slider(
        "Quand es-tu un Génie ?",
        options=["🌅 Matin (5h-11h)", "☀️ Journée (10h-16h)", "🌙 Soir (20h-2h)", "⚡ Par à-coups (Aléatoire)"]
    )
    
    st.subheader("3. Ton Carburant ⛽")
    fuel = st.selectbox(
        "Qu'est-ce qui te fait avancer ?",
        [
            "⚔️ Le Défi (Prouver que je suis le meilleur)",
            "🛡️ La Sécurité (Peur de l'échec)",
            "🎨 Le Sens (Créer du beau/utile)",
            "✅ La Coche (Plaisir de finir une liste)"
        ]
    )
    
    st.divider()
    st.caption("Données confidentielles utilisées uniquement pour la génération.")

# --- PAGE PRINCIPALE ---
st.title("⚡ Chaos Manager")
st.markdown("#### L'IA qui ne te donne pas juste un planning, mais *ta* stratégie.")

# Zone de saisie
user_input = st.text_area(
    "📥 Vide ton cerveau ici (Vrac total accepté) :", 
    height=120, 
    placeholder="Ex: J'ai partiel de physique vendredi, MMA mardi soir, rappeler maman, acheter des pâtes, projet Python à rendre dimanche..."
)

if st.button("🚀 Analyser mon Profil & Générer", type="primary"):
    if not user_input:
        st.warning("Il faut me donner de la matière (tes tâches) !")
    else:
        with st.spinner("Connection neuronale... Profilage en cours..."):
            try:
                # Packaging du profil
                profile = { "pain": pain, "rhythm": rhythm, "fuel": fuel }
                
                # APPEL CERVEAU
                raw_resp = parse_schedule(user_input, profile)
                
                # NETTOYAGE JSON
                cleaned = raw_resp.replace("```json", "").replace("```", "").strip()
                data = json.loads(cleaned)
                
                # --- RÉVÉLATION (GRATUIT) ---
                
                # 1. L'Archétype (Le Miroir)
                archetype_title = data.get('archetype', 'Stratège Inconnu')
                st.markdown(f"""
                <div class="archetype-box">
                    <h3>👤 TON ARCHÉTYPE DÉTECTÉ :</h3>
                    <h2>{archetype_title}</h2>
                </div>
                """, unsafe_allow_html=True)
                
                # 2. Le Planning (La Preuve)
                planning = data.get("planning", [])
                if planning:
                    df = pd.DataFrame(planning)
                    st.dataframe(
                        df[["titre", "start_iso", "end_iso", "categorie"]],
                        use_container_width=True, 
                        hide_index=True
                    )
                
                # --- LE PÉAGE (VERROUILLÉ) ---
                st.markdown("---")
                
                col1, col2 = st.columns([1.5, 1])
                
                with col1:
                    st.markdown('<div class="locked-section">', unsafe_allow_html=True)
                    st.warning("🔒 **Analyse Stratégique Verrouillée**")
                    st.markdown(f"**Pourquoi l'IA t'a identifié comme '{archetype_title}' ?**")
                    
                    # Texte Teaser (Dynamique selon le profil)
                    pain_short = pain.split('(')[0].strip()
                    st.markdown(f"- *Comment contourner ton blocage '{pain_short}'*")
                    st.markdown(f"- *Pourquoi ces horaires sont optimisés pour ton rythme '{rhythm}'*")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    # Texte flouté pour frustrer (dans le bon sens)
                    st.markdown('<p class="blur-text">L analyse montre que ton pic de cortisol est mal géré le matin, c est pourquoi j ai déplacé les tâches complexes à 10h pour maximiser ta dopamine naturelle...</p>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                with col2:
                    st.info("📦 **PACK COMPLET**")
                    st.markdown("""
                    - 📥 Export Agenda (.ics)
                    - 🧠 **Ton Analyse Psycho-Cognitive**
                    - 💡 Stratégie sur-mesure
                    """)
                    
                    # --- TON LIEN STRIPE ICI ---
                    st.link_button(
                        "🔓 DÉBLOQUER (9.90€)", 
                        "https://buy.stripe.com/00w7sN5ZW5gp9GggtP0RG00"
                    )
                    st.caption("Accès immédiat et à vie.")

            except Exception as e:
                st.error(f"Erreur d'analyse : {e}")