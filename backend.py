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

DEBUG_MODE = True # Toujours en mode gratuit pour le dev

def clean_and_parse_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        cleaned_text = match.group(0)
    else:
        return {"error": "Pas de JSON trouvé"}
    try:
        return json.loads(cleaned_text)
    except:
        try:
            return ast.literal_eval(cleaned_text)
        except:
            return {"error": "Échec lecture JSON"}

def parse_schedule(inputs):
    
    # --- MODE SIMULATION ---
    if DEBUG_MODE:
        time.sleep(1.5)
        return json.dumps({
            "scores": {
                "Ouverture": 70, "Conscience": inputs.get('discipline', 30), 
                "Extraversion": 40, "Agreabilite": 60, "Nevrosisme": 80
            },
            "archetype": "Architecte Anxieux",
            "rarity": "Top 5% (Profil Rare)",
            "superpower": "Anticipation des risques",
            "kryptonite": "Paralysie par l'analyse",
            "quote": "Tu as déjà vécu l'échec 1000 fois dans ta tête avant même de commencer.",
            # On ajoute les prompts secrets ici
            "secret_prompts": [
                "Act as a Neuro-Productivity Expert specialized in High Neuroticism profiles.",
                "Use the 'Time-Boxing' technique but add 20% buffer for anxiety management.",
                "Transform every 'Big Goal' into micro-tasks of 15 minutes max."
            ],
            "planning": [
                { "titre": "🌅 Réveil & Ancrage (Pas d'écran)", "start_iso": "2025-12-11T08:00:00", "end_iso": "2025-12-11T08:30:00", "categorie": "Routine", "description": "Calme l'amygdale dès le réveil." },
                { "titre": "🧠 Deep Work : Projet Python (Le plus dur)", "start_iso": "2025-12-11T09:00:00", "end_iso": "2025-12-11T11:00:00", "categorie": "Travail", "description": "Téléphone dans une autre pièce." },
                { "titre": "🍱 Pause Déjeuner & Marche", "start_iso": "2025-12-11T12:00:00", "end_iso": "2025-12-11T13:00:00", "categorie": "Santé", "description": "Lumière du jour obligatoire." },
                { "titre": "MMA (Défouloir)", "start_iso": "2025-12-11T19:00:00", "end_iso": "2025-12-11T20:30:00", "categorie": "Sport", "description": "Évacuation du cortisol." }
            ]
        })

    # --- MODE RÉEL (IA) ---
    # Ici, tu remettras ton prompt complet plus tard
    return json.dumps({"error": "Mode réel désactivé pour économie quota"})

def generate_ics_file(json_data):
    # Code standard inchangé
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