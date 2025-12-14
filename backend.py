import os
import google.generativeai as genai
import datetime
from ics import Calendar, Event
import json
import re
import time
from dotenv import load_dotenv
from google.api_core import exceptions

# --- CONFIGURATION ---
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# MODE MANUEL : True = Lit dummy_data.json / False = Appel API Gemini
DEBUG_MODE = True 

generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", 
    generation_config=generation_config,
)

# --- OUTILS UTILITAIRES ---

def clean_and_parse_json(text):
    """Nettoyeur de JSON robuste"""
    try:
        return json.loads(text)
    except:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            cleaned_text = match.group(0)
            try:
                return json.loads(cleaned_text)
            except:
                pass
    return {"error": "Format JSON invalide", "planning": []}

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

# --- GENERATEUR DE PROMPT (Single Source of Truth) ---

def _build_system_prompt(inputs):
    """Construit le prompt unique pour éviter les duplications."""
    scores = inputs.get("scores", {})
    work_style = inputs.get("work_style", {})
    context = inputs.get("context", {})
    today_date = datetime.date.today().isoformat()

    return f"""
    SYSTEM: Tu es le Chaos Manager, une IA de planification neuro-ergonomique.
    DATE: {today_date}
    
    1. PROFIL COGNITIF (HARDWARE):
    - OCEAN: {json.dumps(scores)}
    - Chronotype: {work_style.get('chronotype')} (Pic d'énergie)
    - Mode Opératoire: {work_style.get('tendency')}
    
    2. MODALITÉS D'INTERVENTION (SOFTWARE):
    - Architecture Requise: {work_style.get('architecture')} 
      (Si 'Technique': focus code/infra. Si 'Éthique': focus valeurs/humain. Si 'Système': focus boucles/entropie.)
    - Zone de Génie: {work_style.get('genius')} 
      (Si 'Idéateur': prévoir phase divergente. Si 'Finisseur': prévoir checklist stricte.)

    3. MISSION & CONTEXTE:
    - Routine Actuelle: {context.get('routine')}
    - Facteurs Limitants: {context.get('blockers')}
    - MISSION IMPÉRATIVE: {context.get('mission')}

    TACHE : Génère le JSON de planification stratégique.
    
    CONTRAINTES:
    - Si Conscience < 30 : Gamifie les titres des tâches.
    - Si Névrosisme > 70 : Ajoute des buffers de sécurité de 15min.
    - Adapte le vocabulaire à l'Architecture choisie.
    
    OUTPUT FORMAT (JSON ONLY):
    {{
        "rarity": "Nom RPG",
        "archetype": "Titre Pro",
        "quote": "Citation",
        "superpower": "Atout",
        "kryptonite": "Faiblesse",
        "analysis_global": "Analyse texte...",
        "analysis_bio": "Analyse texte...",
        "analysis_social": "Analyse texte...",
        "analysis_fogg": "Analyse texte...",
        "chart_energy": [{{"heure": 6, "niveau": 20}}],
        "chart_matrix": [{{"tache": "Exemple", "impact": -50}}],
        "chart_fogg": [{{"tache": "Exemple", "dopamine": 50, "friction": 50, "importance": 50, "zone": "Action", "description": "..."}}],
        "planning": [
            {{
                "titre": "Action",
                "start_iso": "{today_date}T09:00:00",
                "end_iso": "{today_date}T10:00:00",
                "categorie": "DeepWork",
                "description": "Détail"
            }}
        ]
    }}
    """

# --- ORCHESTRATEUR PRINCIPAL ---

def parse_schedule(inputs):
    
    # 1. Génération du Prompt (Centralisée)
    prompt = _build_system_prompt(inputs)

    # 2. Affichage Terminal (Pour copier-coller si besoin)
    print("\n" + "="*40)
    print("🧠 PROMPT GÉNÉRÉ :")
    print("="*40)
    print(prompt) 
    print("="*40 + "\n")

    # 3. BRANCHEMENT
    if DEBUG_MODE:
        print("🔧 MODE DEBUG : Chargement depuis dummy_data.json...")
        try:
            with open("dummy_data.json", "r", encoding="utf-8") as f:
                return f.read() # On renvoie le texte brut du JSON
        except FileNotFoundError:
            return json.dumps({
                "rarity": "ERREUR CONFIG", 
                "archetype": "Fichier dummy_data.json manquant",
                "analysis_global": "Créez le fichier dummy_data.json à la racine.",
                "planning": []
            })
    
    # 4. MODE PROD (API)
    else:
        max_retries = 3
        base_delay = 2 
        print("📡 APPEL API GEMINI EN COURS...")
        
        for attempt in range(max_retries):
            try:
                response = model.generate_content(prompt)
                return response.text
            except exceptions.ResourceExhausted:
                wait_time = base_delay * (2 ** attempt)
                print(f"⚠️ Quota dépassé. Pause de {wait_time}s...")
                time.sleep(wait_time)
            except Exception as e:
                return json.dumps({"error": f"Erreur Technique: {str(e)}"})
        
        return json.dumps({"error": "Quota Saturé - Réessayez plus tard"})