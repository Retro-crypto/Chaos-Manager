import os
import google.generativeai as genai
import datetime
from ics import Calendar, Event
import json
import re
import ast
import time # Pour simuler l'attente
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# --- INTERRUPTEUR MAGIQUE ---
# Mets True pour développer sans payer/attendre (Mode Faux Cerveau)
# Mets False pour la vraie IA (Mode Production)
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
    
    # --- MODE SIMULATION (GRATUIT & ILLIMITÉ) ---
    if DEBUG_MODE:
        time.sleep(2) # On fait semblant que l'IA réfléchit
        # On renvoie une réponse parfaite codée en dur
        fake_response = {
            "scores": {
                "Focus": 95,
                "Discipline": 15,
                "Résilience": 40,
                "Structure": 20,
                "Impulsion": 90
            },
            "archetype": "Visionnaire Impulsif (Simulé)",
            "diagnosis": "MODE DEBUG : Le sujet présente un profil créatif typique. Forte capacité d'hyperfocus nocturne (Focus 95) mais incapacité totale à gérer l'administratif (Structure 20). Le risque de burnout est élevé par cycles.",
            "hack": "Time-Boxing inversé : On ne planifie que les temps de repos, le travail remplit le vide.",
            "planning": [
                { "titre": "Rendu Data Science (Sprint)", "start_iso": "2025-12-09T22:00:00", "end_iso": "2025-12-10T04:00:00", "categorie": "Deep Work", "description": "Sprint nocturne sans interruption." },
                { "titre": "Salle de Sport (Obligatoire)", "start_iso": "2025-12-10T19:00:00", "end_iso": "2025-12-10T20:30:00", "categorie": "Santé", "description": "Sortir de la grotte." },
                { "titre": "Appel Impôts (Douleur)", "start_iso": "2025-12-12T09:00:00", "end_iso": "2025-12-12T09:30:00", "categorie": "Admin", "description": "Faire ça en premier pour s'en débarrasser." }
            ]
        }
        return json.dumps(fake_response)

    # --- MODE RÉEL (IA) ---
    system_instruction = f"""
    Tu es un Expert en Neuro-Productivité.
    ANAMNÈSE :
    1. ÉCHEC : {inputs.get('echec')}
    2. ÉNERGIE : {inputs.get('energie')}
    3. MISSION : {inputs.get('mission')}
    
    TA MISSION : Diagnostic Big Five (0-100), Archétype, Planning JSON.
    FORMAT JSON STRICT :
    {{
        "scores": {{ "Focus": 0, "Discipline": 0, "Résilience": 0, "Structure": 0, "Impulsion": 0 }},
        "archetype": "...",
        "diagnosis": "...",
        "hack": "...",
        "planning": [ {{ "titre": "...", "start_iso": "...", "end_iso": "...", "categorie": "..." }} ]
    }}
    """
    
    # On utilise le modèle Flash GRATUIT quand on n'est pas en Debug
    model = genai.GenerativeModel('gemini-2.0-flash') 
    
    try:
        response = model.generate_content(f"{system_instruction}\nCONTEXTE: {get_current_context()}")
        parsed = clean_and_parse_json(response.text)
        return json.dumps(parsed)
    except Exception as e:
        return json.dumps({"error": str(e)})

def generate_ics_file(json_data):
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