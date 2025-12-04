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

def parse_schedule(user_input):
    # On utilise le modèle Flash pour la rapidité/coût, ou Pro pour la précision
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    current_context = get_current_context()
    
    # LE PROMPT (C'est là que tout se joue)
    prompt = f"""
    CONTEXTE : {current_context}
    
    RÔLE : Tu es un assistant de planification expert. Ta mission est de convertir du texte en vrac en un emploi du temps structuré.
    
    INSTRUCTION : Analyse le texte de l'utilisateur et extrais chaque événement.
    
    RÈGLES STRICTES :
    1. Retourne UNIQUEMENT du JSON valide. Pas de markdown, pas de texte avant ou après.
    2. Format attendu : Une liste d'objets avec les clés : "titre", "start_iso" (format YYYY-MM-DDTHH:MM:SS), "end_iso", "description" (optionnel), "categorie" (ex: Sport, Travail, Santé).
    3. Si la durée n'est pas précisée, estime une durée logique (ex: 1h pour Sport, 30min pour RDV médical).
    4. Gère les récurrences : Si l'utilisateur dit "tous les mardis", génère les occurrences pour les 4 prochaines semaines.
    
    TEXTE UTILISATEUR : "{user_input}"
    """
    
    response = model.generate_content(prompt)
    return response.text

# TEST DU SYSTÈME
if __name__ == "__main__":
    test_input = "J'ai cours de physique demain matin à 8h pendant 2h, et je dois aller au MMA tous les mardis à 19h. Ah et rappelle moi de faire les courses ce samedi."
    
    print("--- ENVOI AU CERVEAU ---")
    print(f"Input : {test_input}")
    
    result = parse_schedule(test_input)
    
    print("\n--- RÉSULTAT JSON ---")
    print(result)

def generate_ics_file(json_data):
    c = Calendar()
    try:
        # On s'assure que json_data est bien une liste (parfois l'IA renvoie un dict)
        if isinstance(json_data, str):
             import json
             events = json.loads(json_data)
        else:
             events = json_data

        for item in events:
            e = Event()
            e.name = item.get("titre", "Événement sans titre")
            e.begin = item.get("start_iso")
            e.end = item.get("end_iso")
            e.description = item.get("description", "")
            # On ajoute la catégorie dans la description pour l'instant
            if item.get("categorie"):
                e.description += f"\n\n[Catégorie: {item['categorie']}]"
            c.events.add(e)
            
        return c.serialize()
    except Exception as e:
        return None