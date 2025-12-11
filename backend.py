import os
import google.generativeai as genai
import datetime
from ics import Calendar, Event
import json
import re
import ast
import time
import random 
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

DEBUG_MODE = False



# Configuration du Modèle (On force le JSON pour la stabilité)
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro", # Ou "gemini-1.5-pro" pour plus de finesse (mais plus lent)
    generation_config=generation_config,
)

def clean_and_parse_json(text):
    """Nettoyeur de JSON robuste"""
    try:
        return json.loads(text)
    except:
        # Cas de secours si le modèle ajoute du markdown ```json ... ```
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            cleaned_text = match.group(0)
            try:
                return json.loads(cleaned_text)
            except:
                pass
    return {"error": "Format JSON invalide renvoyé par l'IA"}

def parse_schedule(inputs):
    
    # --- DIAGNOSTIC CLÉ API ---
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("🚨 ERREUR CRITIQUE : Aucune clé API trouvée dans les variables d'environnement !")
        return json.dumps({"error": "Pas de clé API", "analysis_global": "⚠️ Clé API manquante. Vérifiez le fichier .env"})
    else:
        print(f"✅ Clé API détectée : {api_key[:5]}... (Masquée)")

    # --- MODE SIMULATION ---
    if DEBUG_MODE:
        # ... (Ton code debug existant, ne change rien ici) ...
        print("⚠️ MODE DEBUG ACTIF : Données fictives envoyées.")
        return json.dumps({...}) # Ton code debug existant

    # --- MODE RÉEL (GEMINI) ---
    else:
        print("🧠 Démarrage appel Gemini...")
        
        # ... (Ton extraction de données scores/context) ...
        # Copie bien ton code d'extraction ici
        scores = inputs.get("scores", {})
        work_style = inputs.get("work_style", {})
        context = inputs.get("context", {})
        today_date = datetime.date.today().isoformat()

        # ... (Ton Mega-Prompt user_prompt ici) ...
        # Je ne le remets pas pour gagner de la place, garde le tien
        user_prompt = f"""... TON PROMPT ACTUEL ..."""

        try:
            # 3. Appel à Gemini
            print("📡 Envoi de la requête à Google...")
            response = model.generate_content(user_prompt)
            print("📩 Réponse reçue !")
            
            # DIAGNOSTIC : On affiche la réponse brute dans le terminal
            print(f"📄 CONTENU BRUT DE L'IA : \n{response.text[:200]}...") 

            # 4. Nettoyage et Renvoi
            json_data = clean_and_parse_json(response.text)
            
            if "error" in json_data:
                print(f"❌ Erreur de parsing JSON : {json_data}")
            else:
                print("✅ JSON valide généré avec succès.")

            return json.dumps(json_data)

        except Exception as e:
            print(f"🔥 CRASH GEMINI : {str(e)}")
            return json.dumps({
                "error": f"Erreur Gemini : {str(e)}",
                "planning": [],
                "analysis_global": f"ERREUR TECHNIQUE : {str(e)}", # Affiché à l'utilisateur
                "rarity": "Erreur",
                "archetype": "Hors Ligne"
            })
    




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