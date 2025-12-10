import os
import google.generativeai as genai
import datetime
from ics import Calendar, Event
import json
import re
import ast
import time
import random # Pour la simulation des courbes
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
        # Récupération des données riches
        work_style = inputs.get("work_style", {})
        animal = work_style.get("chronotype", "Ours").split(" ")[1] # On garde juste "Lion"
        profil_rubin = work_style.get("tendency", "Questioner").split(" ")[1] # On garde juste "Questioner"
        
        # Logique de simulation simple pour le titre
        archetype_name = f"{animal} {profil_rubin}"
        
        return json.dumps({
            "rarity": "Profil Neuro-Cross Rare",
            "archetype": archetype_name, # Ex: "Lion Rebel"
            "superpower": "Démarrage Explosif",
            "kryptonite": "Contraintes externes",
            "quote": "Votre énergie est nucléaire, ne la gâchez pas sur des tâches administratives le matin.",
            "planning": [
                { "titre": "Deep Work (Pic Cortisol)", "start_iso": "2025-12-11T08:00:00", "end_iso": "2025-12-11T11:00:00", "categorie": "Travail", "description": "Zone de génie activée." },
                { "titre": "Déjeuner", "start_iso": "2025-12-11T12:00:00", "end_iso": "2025-12-11T13:00:00", "categorie": "Santé", "description": "Pause." }
            ],
            # On ajoute des prompts secrets plus crédibles
            "secret_prompts": [
                f"Applying '{animal}' chronotype: Shift peak cognitive load to biologically optimal window.",
                f"Applying '{profil_rubin}' framework: Rephrase all tasks as personal challenges rather than obligations.",
                "Algorithm: Neuro-Cross V6.1 Optimized."
            ]
        })

    # --- MODE RÉEL ---
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