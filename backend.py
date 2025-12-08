import os
import google.generativeai as genai
import datetime
from ics import Calendar, Event
import json
import re  # On importe les expressions régulières pour le nettoyage chirurgical
from dotenv import load_dotenv

# Chargement des variables (si local)
load_dotenv()

# Configuration API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_current_context():
    now = datetime.datetime.now()
    return f"Nous sommes le {now.strftime('%A %d %B %Y')}. L'heure actuelle est {now.strftime('%H:%M')}."

def clean_json_response(text):
    """
    Fonction de nettoyage chirurgical.
    Elle cherche le premier '{' et le dernier '}' pour extraire uniquement le JSON,
    ignorant le blabla avant ou après.
    """
    try:
        # On cherche le pattern JSON
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return match.group(0)
        else:
            return text # Si on trouve rien, on renvoie tel quel (ça plantera plus loin mais on saura pourquoi)
    except:
        return text

def parse_schedule(user_input, user_profile):
    system_instruction = f"""
    Tu es un Expert en Productivité et Psychologie.
    
    PROFIL UTILISATEUR :
    - Frein : {user_profile.get('pain', 'Non défini')}
    - Rythme : {user_profile.get('rhythm', 'Non défini')}
    - Moteur : {user_profile.get('fuel', 'Non défini')}
    
    MISSION :
    1. Analyse les tâches.
    2. Crée un planning JSON.
    3. Trouve un ARCHÉTYPE percutant.
    4. Rédige une analyse psycho.
    
    FORMAT JSON STRICT :
    {{
        "planning": [
            {{ "titre": "...", "start_iso": "YYYY-MM-DDTHH:MM:SS", "end_iso": "...", "categorie": "...", "description": "..." }}
        ],
        "archetype": "Titre Stylé",
        "analysis": "Ton analyse ici..."
    }}
    """
    
    # ON UTILISE LA ROLLS ROYCE (Stable et Intelligente)
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    full_prompt = f"{system_instruction}\n\nCONTEXTE: {get_current_context()}\n\nINPUT: {user_input}"
    
    try:
        response = model.generate_content(full_prompt)
        # On nettoie la réponse avant de la renvoyer
        return clean_json_response(response.text)
    except Exception as e:
        return f"{{ 'error': 'Erreur API : {e}' }}"

def generate_ics_file(json_data):
    c = Calendar()
    try:
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