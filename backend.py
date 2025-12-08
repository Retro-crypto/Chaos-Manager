import os
import google.generativeai as genai
import datetime
from ics import Calendar, Event
import json
import re
import ast
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

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
    # inputs est un dictionnaire avec les 3 réponses
    
    system_instruction = f"""
    Tu es un Expert en Neuro-Productivité et Psychologie Comportementale.
    
    ANAMNÈSE DU PATIENT (Tes données) :
    1. SON ÉCHEC PASSÉ (Facteurs Limitants) : {inputs.get('echec', 'Non précisé')}
    2. SON ÉNERGIE (Moteur Interne) : {inputs.get('energie', 'Non précisé')}
    3. SA MISSION (Tâches à faire) : {inputs.get('mission', 'Non précisé')}
    
    TA MISSION :
    1. Établis un DIAGNOSTIC PSYCHOLOGIQUE (Score de 0 à 100 sur les 5 axes Big Five Productivité).
    2. Identifie son ARCHÉTYPE (Titre clinique, ex: "Architecte Perfectionniste à Risque de Burnout").
    3. Crée le planning optimal pour contourner ses failles.
    
    FORMAT JSON STRICT ATTENDU :
    {{
        "scores": {{
            "Focus": 85,
            "Discipline": 40,
            "Résilience": 60,
            "Structure": 30,
            "Impulsion": 90
        }},
        "archetype": "Nom de l'archétype",
        "diagnosis": "Analyse clinique de ses failles...",
        "hack": "Le hack cognitif spécifique utilisé pour ce planning...",
        "planning": [
            {{ "titre": "...", "start_iso": "YYYY-MM-DDTHH:MM:SS", "end_iso": "...", "categorie": "...", "description": "..." }}
        ]
    }}
    """
    
    model = genai.GenerativeModel('gemini-2.0-flash')
    full_prompt = f"{system_instruction}\n\nCONTEXTE: {get_current_context()}"
    
    try:
        response = model.generate_content(full_prompt)
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
            if item.get("categorie"):
                e.description += f"\n[Type: {item['categorie']}]"
            c.events.add(e)
        return c.serialize()
    except:
        return None