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

DEBUG_MODE = True 

def clean_and_parse_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match: cleaned_text = match.group(0)
    else: return {"error": "Pas de JSON trouvé"}
    try: return json.loads(cleaned_text)
    except:
        try: return ast.literal_eval(cleaned_text)
        except: return {"error": "Échec lecture JSON"}

def parse_schedule(inputs):
    
    # --- MODE SIMULATION ---
    if DEBUG_MODE:
        time.sleep(1.5)
        # On récupère les scores OCEAN passés par l'app
        scores = inputs.get("scores", {})
        
        # Simulation d'un archétype basé sur les habitudes
        work_style = inputs.get("work_style", {})
        focus = work_style.get("focus", "Standard")
        
        archetype_name = "Stratège"
        if "Hyperfocus" in focus: archetype_name = "Visionnaire Obsessif"
        elif "TDAH" in focus: archetype_name = "Explorateur Chaotique"
        
        return json.dumps({
            "rarity": "Profil Hybride Rare",
            "archetype": archetype_name,
            "superpower": "Flux Cognitif Rapide",
            "kryptonite": "Ennui & Routine",
            "quote": "Votre cerveau est une Formule 1, ne le conduisez pas comme une Twingo.",
            "planning": [
                { "titre": "Mise en route (Douceur)", "start_iso": "2025-12-11T09:00:00", "end_iso": "2025-12-11T09:30:00", "categorie": "Routine", "description": "Pas de pression." },
                { "titre": "Deep Work : Projet Prioritaire", "start_iso": "2025-12-11T09:30:00", "end_iso": "2025-12-11T12:30:00", "categorie": "Travail", "description": "Mode avion activé." },
                { "titre": "Déjeuner", "start_iso": "2025-12-11T12:30:00", "end_iso": "2025-12-11T13:30:00", "categorie": "Santé", "description": "Pause." }
            ]
        })

    # --- MODE RÉEL (A ACTIVER PLUS TARD) ---
    # Ici le prompt devra combiner inputs['scores'] et inputs['work_style']
    return json.dumps({"error": "Mode réel désactivé"})

def generate_ics_file(json_data):
    c = Calendar()
    try:
        if isinstance(json_data, str): data = json.loads(json_data)
        else: data = json_data
        for item in data.get("planning", []):
            e = Event()
            e.name = item.get("titre", "Event")
            e.begin = item.get("start_iso")
            e.end = item.get("end_iso")
            c.events.add(e)
        return c.serialize()
    except: return None