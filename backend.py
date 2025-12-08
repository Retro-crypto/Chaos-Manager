import os
import google.generativeai as genai
import datetime
from ics import Calendar, Event
import json

# Configuration API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_current_context():
    now = datetime.datetime.now()
    return f"Nous sommes le {now.strftime('%A %d %B %Y')}. L'heure actuelle est {now.strftime('%H:%M')}."

def parse_schedule(user_input, user_profile):
    # On construit le prompt psychologique
    system_instruction = f"""
    Tu es un Expert en Productivité et en Psychologie Comportementale.
    
    PROFIL DE L'UTILISATEUR (Ce qu'il t'a avoué) :
    - Son Frein Principal : {user_profile['pain']}
    - Son Rythme Biologique : {user_profile['rhythm']}
    - Son Carburant (Motivation) : {user_profile['fuel']}
    
    TA MISSION :
    1. Analyse ses contraintes (texte) à travers le prisme de son profil.
    2. Crée un planning JSON réaliste.
    3. DÉFINIS SON ARCHÉTYPE (Un titre cool et percutant, ex: "Stratège Nocturne", "Guerrier de l'Urgence").
    4. Rédige une analyse (pourquoi ce planning est fait pour lui).
    
    FORMAT JSON ATTENDU (STRICT) :
    {{
        "planning": [
            {{ "titre": "...", "start_iso": "YYYY-MM-DDTHH:MM:SS", "end_iso": "...", "categorie": "...", "description": "..." }}
        ],
        "archetype": "Le Titre de son Archétype",
        "analysis": "L'explication psychologique et stratégique..."
    }}
    """
    
    model = genai.GenerativeModel('gemini-2.5-flash')
    full_prompt = f"{system_instruction}\n\nCONTEXTE TEMPOREL: {get_current_context()}\n\nCONTRAINTES UTILISATEUR : {user_input}"
    
    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Erreur API : {e}"

def generate_ics_file(json_data):
    c = Calendar()
    try:
        # Gestion robuste : soit on reçoit le dict complet, soit juste la liste
        data_source = json_data.get("planning", []) if isinstance(json_data, dict) else json_data
        
        for item in data_source:
            e = Event()
            e.name = item.get("titre", "Event")
            e.begin = item.get("start_iso")
            e.end = item.get("end_iso")
            e.description = item.get("description", "")
            if item.get("categorie"):
                e.description += f"\n[Type: {item['categorie']}]"
            c.events.add(e)
        return c.serialize()
    except Exception as e:
        return None