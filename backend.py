import os
import google.generativeai as genai
import json
import random
import datetime
from ics import Calendar, Event
from dotenv import load_dotenv

load_dotenv()

# Configuration Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
generation_config = {
    "temperature": 0.9,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
}
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# --- CONFIGURATION ---
DEBUG_MODE = True  # METTRE A FALSE POUR ACTIVER L'IA RÉELLE

def build_system_instruction(inputs):
    """
    C'est la NOUVELLE fonction qui construit le prompt intelligent.
    Elle n'existait pas avant. Elle traduit le profil OCEAN en instructions.
    """
    scores = inputs.get('scores', {})
    ws = inputs.get('work_style', {})
    
    # 1. ANALYSE DU PROFIL
    # On définit des booléens pour simplifier la logique
    is_chaotic = scores.get('Conscience', 50) < 30
    is_neurotic = scores.get('Névrosisme', 50) > 70
    is_night_owl = "Loup" in ws.get('chronotype', '') or "Dauphin" in ws.get('chronotype', '')
    is_rebel = "Rebel" in ws.get('tendency', '')

    # 2. CONSTRUCTION DES MODULES STRATÉGIQUES
    strategy_modules = []

    # Module A: Gestion du Temps
    if is_night_owl:
        strategy_modules.append("⏳ **TIME SHIFTING:** User has delayed circadian phase. DO NOT schedule cognitive load before 10:00 AM. Push high-value tasks to late afternoon/night.")
    elif is_chaotic:
        strategy_modules.append("⏱️ **POMODORO SPRINT:** User cannot sustain focus. Break all tasks into 25-minute sprints with mandatory movement breaks.")
    else:
        strategy_modules.append("📅 **LINEAR BLOCKING:** User requires standard 90-minute blocks.")

    # Module B: Ton & Psychologie
    if is_rebel:
        strategy_modules.append("🛡️ **AUTONOMY FRAMING:** DO NOT give orders. Use 'Options' and 'Challenges'. Example: Instead of 'Do report', use 'Challenge: Beat the report in 30min'.")
    elif is_neurotic:
        strategy_modules.append("🧣 **ANXIETY REDUCTION:** Use reassuring language. Add 'Buffer Time' before deadlines. Focus on ONE major victory per day.")
    else:
        strategy_modules.append("⚔️ **COMMANDER MODE:** Be direct, dry, and efficient. No fluff.")

    # 3. ASSEMBLAGE DU PROMPT FINAL
    prompt = f"""
    ROLE: You are the Chaos Manager, an elite scheduler for neuro-divergent profiles.
    
    USER BIOMETRICS:
    - OCEAN Vector: {json.dumps(scores)}
    - Chronotype: {ws.get('chronotype')}
    - Psychology: {ws.get('tendency')}
    
    >>> ACTIVE STRATEGIC PROTOCOLS (STRICT ENFORCEMENT):
    {chr(10).join(strategy_modules)}
    
    MISSION:
    Parse the user's raw input: "{inputs.get('mission')}"
    
    EXECUTION:
    1. Filter trivial tasks if the list is too long.
    2. Map tasks to the user's energy curve (defined by protocols above).
    3. Generate the JSON schedule.
    
    OUTPUT FORMAT (JSON ONLY):
    {{
        "rarity": "Title (e.g. 'Midnight Architect')",
        "archetype": "Archetype Name",
        "superpower": "Main Strength",
        "kryptonite": "Main Weakness",
        "quote": "Personalized advice based on protocols.",
        "planning": [
            {{
                "titre": "Action title",
                "start_iso": "YYYY-MM-DDTHH:MM:SS",
                "end_iso": "YYYY-MM-DDTHH:MM:SS",
                "categorie": "Travail | Santé | Social | Admin",
                "description": "Short rationale."
            }}
        ]
    }}
    CONSTRAINTS:
    - Use today's date: {datetime.date.today().isoformat()} as base.
    """
    return prompt

def parse_schedule(inputs):
    """
    Fonction principale qui choisit entre SIMULATION (Debug) et IA (Prod)
    """
    
    # --- A. MODE SIMULATION (GRATUIT & RAPIDE) ---
    # --- A. MODE SIMULATION (GRATUIT & RAPIDE) ---
    if DEBUG_MODE:
        # Récupération des inputs
        scores = inputs.get("scores", {})
        e_score = scores.get("Extraversion", 50)
        c_score = scores.get("Conscience", 50)
        n_score = scores.get("Névrosisme", 50)
        chrono = inputs.get("work_style", {}).get("chronotype", "🐻 Ours")
        
        # 1. GENERATION TEXTE : ANALYSE GLOBALE (Tab 1)
        if c_score > 70:
            txt_global = "Votre haute Conscience permet une architecture rigide. Le planning ci-dessous minimise l'incertitude."
        elif c_score < 30:
            txt_global = "Votre profil divergent nécessite de la variété. Nous avons fragmenté les blocs pour maintenir la dopamine."
        else:
            txt_global = "Profil équilibré détecté. Le planning alterne focus et flexibilité pour optimiser l'endurance."

        # 2. GENERATION TEXTE : ANALYSE BIO (Tab 2)
        if "Lion" in chrono:
            peak_hour = 9
            txt_bio = "En tant que Lion, votre fenêtre de tir cognitive est matinale (07h-11h). C'est là que votre cortisol est un super-carburant."
        elif "Loup" in chrono:
            peak_hour = 19
            txt_bio = "Votre chronotype Loup indique une inertie matinale. L'IA a repoussé les tâches lourdes pour s'aligner sur votre pic du soir."
        elif "Dauphin" in chrono:
            peak_hour = 15
            txt_bio = "Votre sommeil fragile (Dauphin) rend votre énergie erratique. Le planning vise des sprints courts plutôt qu'un marathon."
        else: # Ours
            peak_hour = 12
            txt_bio = "Votre biorythme solaire (Ours) est stable. L'objectif est de protéger le pic de 10h-14h contre les interruptions."
            
        # Simulation Courbe
        energy_curve = []
        for h in range(6, 24):
            dist = abs(h - peak_hour)
            level = max(10, 100 - (dist * 10) + random.randint(-5, 5))
            energy_curve.append({"heure": h, "niveau": level})

        # 3. GENERATION TEXTE : ANALYSE SOCIALE (Tab 3)
        social_impact = (e_score - 50) * 2 
        if e_score < 30:
            txt_social = "⚠️ Alerte Introversion : Les interactions humaines sont coûteuses pour vous. 1h de réunion consomme autant de batterie que 2h de code."
        elif e_score > 70:
            txt_social = "✅ Moteur Social : L'isolement vous vide. Le planning doit inclure des interactions pour recharger votre batterie."
        else:
            txt_social = "Profil Ambivert : Vous tolérez bien les réunions, mais elles ne doivent pas empiéter sur le Deep Work."

        matrix_data = [
            {"tache": "Réunions / Brainstorm", "impact": social_impact, "type": "Social"},
            {"tache": "Deep Work Solitaire", "impact": -social_impact, "type": "Focus"},
            {"tache": "Admin / Routine", "impact": -20, "type": "Neutre"},
            {"tache": "Urgence / Crise", "impact": n_score * -1, "type": "Stress"},
        ]

        # 4. RETOUR JSON ENRICHI
        return json.dumps({
            "rarity": "TEST MODE ACTIF",
            "archetype": f"Simulateur : {chrono.split(' ')[1] if ' ' in chrono else chrono}",
            "superpower": "Itération Rapide",
            "kryptonite": "Pas d'IA réelle",
            "quote": "Ceci est une simulation. Changez DEBUG_MODE en False pour l'intelligence réelle.",
            "planning": [
                { "titre": "🌞 Activation Matinale", "start_iso": "2025-12-12T07:30:00", "end_iso": "2025-12-12T08:00:00", "categorie": "Santé", "description": "Lumière & Protéines." },
                { "titre": "🧠 Deep Work (Pic)", "start_iso": "2025-12-12T09:00:00", "end_iso": "2025-12-12T11:30:00", "categorie": "Travail", "description": "Tâche principale sans distraction." },
                { "titre": "🥗 Pause Déjeuner", "start_iso": "2025-12-12T12:00:00", "end_iso": "2025-12-12T13:00:00", "categorie": "Santé", "description": "Recharge." },
                { "titre": "⚡ Admin Burst", "start_iso": "2025-12-12T14:00:00", "end_iso": "2025-12-12T15:00:00", "categorie": "Admin", "description": "Emails et factures." },
                { "titre": "🔄 Reset Cognitif", "start_iso": "2025-12-12T16:00:00", "end_iso": "2025-12-12T16:20:00", "categorie": "Santé", "description": "Marche ou NSDR." }
            ],
            "chart_energy": energy_curve,
            "chart_matrix": matrix_data,
            # NOUVEAUX CHAMPS TEXTE
            "analysis_global": txt_global,
            "analysis_bio": txt_bio,
            "analysis_social": txt_social
        })

    # --- B. MODE RÉEL (GEMINI) ---
    try:
        final_prompt = build_system_instruction(inputs)
        response = model.generate_content(final_prompt)
        return response.text 
    except Exception as e:
        return json.dumps({
            "rarity": "API ERROR",
            "archetype": "System Failure",
            "quote": str(e),
            "planning": []
        })

def generate_ics_file(json_data):
    c = Calendar()
    try:
        if isinstance(json_data, str): data = json.loads(json_data)
        else: data = json_data
        for item in data.get("planning", []):
            e = Event()
            e.name = item.get("titre", "Event")
            try:
                e.begin = item.get("start_iso")
                e.end = item.get("end_iso")
            except:
                continue
            e.description = item.get("description", "")
            c.events.add(e)
        return c.serialize()
    except: return None