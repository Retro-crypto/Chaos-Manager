import os
import google.generativeai as genai
import datetime
from ics import Calendar, Event
import json
import re
import ast  # <--- La nouvelle arme secrète
from dotenv import load_dotenv

# Chargement des variables (si local)
load_dotenv()

# Configuration API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_current_context():
    now = datetime.datetime.now()
    return f"Nous sommes le {now.strftime('%A %d %B %Y')}. L'heure actuelle est {now.strftime('%H:%M')}."

def clean_and_parse_json(text):
    """
    Fonction intelligente qui tente de réparer le JSON malformé.
    """
    # 1. On extrait le bloc entre accolades {}
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        cleaned_text = match.group(0)
    else:
        return {"error": "Pas de JSON trouvé"}

    # 2. Tentative 1 : JSON Standard (Strict)
    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError:
        pass # On ne panique pas, on passe au plan B

    # 3. Tentative 2 : Format Python (Simple Quotes)
    try:
        return ast.literal_eval(cleaned_text)
    except Exception as e:
        return {"error": f"Échec lecture JSON: {e}"}

def parse_schedule(user_input, user_profile):
    system_instruction = f"""
    Tu es un Expert en Productivité.
    
    PROFIL :
    - Frein : {user_profile.get('pain', 'Non défini')}
    - Rythme : {user_profile.get('rhythm', 'Non défini')}
    - Moteur : {user_profile.get('fuel', 'Non défini')}
    
    TACHE :
    Génère un planning adapté et une analyse.
    
    IMPORTANT : Réponds UNIQUEMENT avec un JSON valide. Utilise des guillemets doubles (") pour les clés et les textes.
    
    FORMAT JSON :
    {{
        "planning": [
            {{ "titre": "Titre", "start_iso": "YYYY-MM-DDTHH:MM:SS", "end_iso": "...", "categorie": "Travail", "description": "..." }}
        ],
        "archetype": "Nom de l'archétype",
        "analysis": "Analyse..."
    }}
    """
    
    # On garde le modèle Pro, il est meilleur
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    full_prompt = f"{system_instruction}\n\nCONTEXTE: {get_current_context()}\n\nINPUT: {user_input}"
    
    try:
        response = model.generate_content(full_prompt)
        # On utilise notre nouvelle fonction de parsing robuste
        parsed_data = clean_and_parse_json(response.text)
        
        # Si la fonction retourne le dictionnaire directement, on le renvoie en string JSON pour l'app
        return json.dumps(parsed_data)
        
    except Exception as e:
        return json.dumps({"error": f"Erreur API : {e}"})

def generate_ics_file(json_data):
    c = Calendar()
    try:
        # On s'assure d'avoir un dictionnaire
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
            if item.get("categorie"):
                e.description += f"\n[Type: {item['categorie']}]"
            c.events.add(e)
        return c.serialize()
    except Exception as e:
        return None