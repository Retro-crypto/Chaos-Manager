import os
import google.generativeai as genai
import datetime
from ics import Calendar, Event
import json
import re
import ast
import time
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# --- RESTE EN TRUE POUR CODER L'INTERFACE GRATUITEMENT ---
DEBUG_MODE = True 

def get_current_context():
    now = datetime.datetime.now()
    return f"Date: {now.strftime('%A %d %B %Y')}. Heure: {now.strftime('%H:%M')}."

def clean_and_parse_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        cleaned_text = match.group(0)
    else:
        return {"error": "Pas de JSON trouvé"}
    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError:
        try:
            return ast.literal_eval(cleaned_text)
        except:
            return {"error": "Échec lecture JSON"}

def parse_schedule(inputs):
    
    # --- MODE SIMULATION (POUR LE DEV UI) ---
    if DEBUG_MODE:
        time.sleep(1.5)
        # On simule une réponse basée sur les sliders (Approximation)
        # C'est juste pour tester l'affichage "Carte RPG"
        fake_response = {
            "scores": {
                "Focus": 85,
                "Discipline": inputs.get('discipline', 30), # On reprend la valeur du slider
                "Résilience": 40,
                "Structure": 20,
                "Impulsion": 90
            },
            "archetype": "Berserker Nocturne",
            "rarity": "Top 4% (Profil Rare)",
            "superpower": "Hyperfocus en urgence",
            "kryptonite": "L'ennui administratif",
            "quote": "Tu es capable de déplacer des montagnes en une nuit, mais tu trébuches sur un caillou le lendemain.",
            "planning": [
                { "titre": "Sprint Deep Work", "start_iso": "2025-12-10T22:00:00", "end_iso": "2025-12-10T23:30:00", "categorie": "Travail", "description": "Mode guerre." },
                { "titre": "Repos Forcé", "start_iso": "2025-12-11T10:00:00", "end_iso": "2025-12-11T11:00:00", "categorie": "Santé", "description": "Récupération." }
            ]
        }
        return json.dumps(fake_response)

    # --- MODE RÉEL (IA) ---
    system_instruction = f"""
    Tu es un Profiler Psychologique Expert.
    
    DONNÉES PATIENT :
    - Énergie : {inputs.get('energy')}
    - Chronotype : {inputs.get('chronotype')}
    - Discipline (Auto-évaluation /100) : {inputs.get('discipline')}
    - Focus Type : {inputs.get('focus')}
    - Réaction Stress : {inputs.get('stress')}
    - Peur Secrète : {inputs.get('fear')}
    - Mission : {inputs.get('mission')}
    
    TA MISSION :
    1. Calcule les Scores Big Five Productivité (0-100).
    2. Crée un PROFIL RPG (Archétype, Rareté, Pouvoir, Faiblesse).
    3. Génère le planning.
    
    FORMAT JSON STRICT :
    {{
        "scores": {{ "Focus": X, "Discipline": X, "Résilience": X, "Structure": X, "Impulsion": X }},
        "archetype": "Titre Épique (ex: Architecte de Cristal)",
        "rarity": "Top X% (ex: Top 2% Population)",
        "superpower": "Son atout majeur",
        "kryptonite": "Sa faiblesse fatale",
        "quote": "Une phrase choc qui résume sa vie.",
        "planning": [ ... ]
    }}
    """
    
    # On utilise le modèle Flash GRATUIT (si quota dispo)
    model = genai.GenerativeModel('gemini-2.0-flash') 
    
    try:
        response = model.generate_content(f"{system_instruction}\nCONTEXTE: {get_current_context()}")
        parsed = clean_and_parse_json(response.text)
        return json.dumps(parsed)
    except Exception as e:
        return json.dumps({"error": str(e)})

def generate_ics_file(json_data):
    # (Même code qu'avant, pas de changement ici)
    c = Calendar()
    try:
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
        events = data.get("planning", [])
        for item in events:
            e = Event()
            e.name = item.get("titre", "Event")
            e.begin = item.get("start_iso")
            e.end = item.get("end_iso")
            e.description = item.get("description", "")
            c.events.add(e)
        return c.serialize()
    except:
        return None