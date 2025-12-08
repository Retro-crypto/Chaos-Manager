import os
import datetime
import google.generativeai as genai
from dotenv import load_dotenv
from ics import Calendar, Event

# Charger les variables d'environnement
load_dotenv()

# Configurer l'API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_current_context():
    now = datetime.datetime.now()
    # On donne le jour de la semaine et la date précise pour aider l'IA
    return f"Nous sommes le {now.strftime('%A %d %B %Y')}. L'heure actuelle est {now.strftime('%H:%M')}."

# backend.py (Mise à jour)

def parse_schedule(user_input, preferences):
    # On construit un contexte riche avec les préférences de l'utilisateur
    system_instruction = f"""
    Tu es un assistant d'organisation d'élite.
    
    PARAMÈTRES UTILISATEUR :
    - Intensité des blocs de travail : {preferences['intensity']}
    - Préférence de répartition : {preferences['distribution']}
    - Heure de lever : {preferences['wake_up']}
    
    TA MISSION :
    1. Analyse le texte de l'utilisateur (ses contraintes).
    2. Génère une liste d'événements JSON précise (dates ISO 8601).
    3. Rédige un "Conseil Stratégique" (coach_message) qui explique pourquoi tu as agencé la semaine comme ça, en t'adaptant à son profil. Sois percutant, tutoie-le.
    
    FORMAT DE RÉPONSE ATTENDU (JSON STRICT SEULEMENT) :
    {{
        "planning": [
            {{ "titre": "...", "start_iso": "YYYY-MM-DDTHH:MM:SS", "end_iso": "...", "categorie": "Travail/Sport/Perso", "description": "..." }}
        ],
        "coach_message": "Ton message d'analyse ici..."
    }}
    """
    
    # Appel à Gemini (Flash est suffisant)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # On combine les instructions et l'input
    full_prompt = f"{system_instruction}\n\nINPUT UTILISATEUR : {user_input}"
    
    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Erreur API : {e}"

# ATTENTION : Il faut aussi adapter légèrement la fonction ICS pour qu'elle lise la nouvelle structure
def generate_ics_file(json_data):
    c = Calendar()
    try:
        # Si json_data est le dictionnaire complet, on prend juste la liste "planning"
        events_list = json_data.get("planning", []) if isinstance(json_data, dict) else json_data
        
        for item in events_list:
            e = Event()
            e.name = item.get("titre", "Event")
            e.begin = item.get("start_iso")
            e.end = item.get("end_iso")
            e.description = item.get("description", "")
            c.events.add(e)
        return c.serialize()
    except Exception as e:
        return None

