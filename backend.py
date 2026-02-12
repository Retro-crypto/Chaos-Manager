import google.generativeai as genai
import streamlit as st
import datetime
from ics import Calendar, Event
import json
import time
import random
from dotenv import load_dotenv
from google.oauth2 import service_account
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re



genai.configure(api_key = st.secrets["general"]["GEMINI_API_KEY"])

generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
}

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash", 
    generation_config=generation_config,
)




def clean_and_parse_json(raw_text):
    """
    Nettoie la réponse de Gemini pour extraire le JSON pur,
    même si le modèle bavarde ou met des balises Markdown.
    """
    try:
        # 1. Suppression des balises Markdown (```json ... ```)
        text = re.sub(r"```json\s*", "", raw_text, flags=re.IGNORECASE)
        text = re.sub(r"```", "", text)
        
        # 2. Parsing
        return json.loads(text)
    
    except json.JSONDecodeError as e:
        # LOG DE DEBUG CRITIQUE (Pour voir ce qui a cassé dans la console)
        print(f"🚨 ERREUR JSON: {e}")
        print(f"💀 TEXTE REÇU: {raw_text[:500]}...") # On affiche le début pour comprendre
        return None
    

def _get_teaser_prompt(inputs):
    scores = inputs.get("scores", {})
    work_style = inputs.get("work_style", {})
    
    return f"""
    ROLE : Neuro-Architecte d'Élite & Bio-hacker.
    TON : Fascinant, Autoritaire, "No-Bullshit". Tu es celui qui détient la clé du code source de leur cerveau.
    
    INPUT CIBLE :
    - OCEAN : {json.dumps(scores)}
    - Chronotype : {work_style.get('chronotype')}
    - Profil : {work_style.get('architecture')}
    
    OBJECTIF : Générer le JSON de conversion pour la Landing Page.
    
    1. "archetype": CORRÉLATION MBTI ESTIMÉE.
       - Analyse les scores OCEAN pour déduire le profil MBTI le plus probable (E/I, N/S, T/F, J/P).
       - Format : "CODE - Le Nom" (ex: "ENTP - Le Visionnaire", "INFJ - L'Avocat").
       - Sois cohérent : Score O élevé = N, Score C bas = P, etc.
    
    2. "rarity": SIGNATURE COGNITIVE (Pas de stat inventée).
       - Identifie les 2 traits les plus marquants du profil (soit très élevés, soit très bas).
       - Crée une étiquette qui résume cette tension.
       - Exemples : "Haute Créativité / Faible Structure", "Empathie Radicale / Sensibilité au Stress", "Logique Implacable / Introversion Sociale".
       - C'est ça qui rend le profil "unique", pas un chiffre au hasard.
    
    3. "teaser_html": LE DIAGNOSTIC 20/80 (environ 250 mots).
       - OBJECTIF : Appliquer la Loi de Pareto. Identifie LE trait de personnalité dominant (parmi ses scores) qui cause 80% de ses échecs avec les méthodes classiques.
       
       - PARTIE A (La Friction Biologique) : 
         Ne fais pas un cours général. Adresse-toi à LUI.
         Explique pourquoi un agenda linéaire (9h-18h) est toxique *spécifiquement pour son profil*.
         * Si "Conscience" basse : Explique que la rigidité crée du cortisol qui bloque son action.
         * Si "Ouverture" haute : Explique que la routine tue sa dopamine et donc sa motivation.
         * Si "Névrosisme" haut : Explique que la pression matinale épuise ses réserves avant midi.
         Utilise des termes comme "Friction neuronale", "Coût métabolique", "Cycle d'énergie inversé".
         
       - PARTIE B (Le Pivot Stratégique) : 
         Introduis la solution non pas comme un "effort" mais comme un "réglage".
         "Votre erreur n'est pas le manque de volonté, c'est le mauvais timing. Pour obtenir 80% de résultats en plus avec 20% d'effort en moins, nous ne devons pas changer qui vous êtes, nous devons synchroniser vos tâches avec votre pic hormonal..."
         
       - IMPORTANT : Le texte doit s'arrêter net au milieu de la phrase qui allait révéler LE secret de son planning (les "..." dramatiques).
    
    4. "preview_day": L'ARCHITECTURE 80/20 (3 ou 4 blocs CLÉS seulement).
       - RÈGLE D'OR (Adaptation Charge) :
         * Si le score "Conscience" (Organisation) est < 40/100 : Ne mets JAMAIS plus de 1 seul bloc de Deep Work pur. Le reste doit être du "Sprint" ou de la "Créativité". Pas de discipline militaire.
         * Si le score "Névrosisme" (Stress) est > 60/100 : Le premier bloc ne doit jamais être une tâche anxiogène (Admin/Urgence), mais une tâche "Starter" (Dopamine).
       
       - RÈGLE DU 80/20 (Le Pareto) :
         * Un des blocs doit être identifié comme la "GOLDEN ZONE". C'est le moment où sa biologie permet d'abattre 80% du travail de la journée en 90 minutes.

       - FORMAT JSON POUR CHAQUE BLOC :
         * "time": Heure adaptée au Chronotype (Loup = Tard, Lion = Tôt).
         * "phase": Titre Orienté Résultat (ex: "Le Levier 80/20", "Vidange Cortisol", "Sprint Créatif").
         * "tag_visible": Une petite phrase courte visible (ex: "Impact Maximal • Zone de Génie").
         * "neuro_logic": (CECI SERA FLOUTÉ). C'est l'explication neuro-stratégique.
           Ne donne pas de conseil gadget (lumière/son).
           Explique le lien Tâche <-> Hormone.
           Exemple Admin : "Votre taux de cortisol est naturellement haut à cette heure. C'est le carburant idéal pour 'tuer' les tâches administratives sans douleur. Le faire plus tard vous coûterait 3x plus d'énergie."
           Exemple Créa : "Votre cortex préfrontal est inhibé, laissant place aux connexions abstraites. C'est le seul moment pour la stratégie."
    5. "DATA VISUALISATION" (La Preuve par l'Image).
       - chart_energy (Courbe Circadienne) :
         * DOIT respecter le Chronotype détecté !
         * Si "Loup" (Soir) : Pic principal vers 18h-20h. Creux le matin.
         * Si "Lion" (Matin) : Pic principal vers 07h-09h. Crash à 15h.
         * Si "Ours" (Normal) : Pic vers 11h et 16h.
         * L'utilisateur doit voir graphiquement que son énergie n'est PAS linéaire.

       - chart_matrix (Matrice d'Impact) :
         * Génère 5 points représentant des tâches typiques.
         * Si score "Conscience" < 40 : Mets en avant des tâches "Quick Wins" (Faible Effort / Gros Impact) pour le motiver.
         * Si score "Névrosisme" > 60 : Évite les tâches à "Haute Pression".

       - chart_fogg (Motivation vs Friction) :
         * Place un point "Projet de Rêve" (celui qu'il procrastine).
         * Si "Ouverture" est haute mais "Conscience" basse : Place le point dans la zone "Haute Motivation" mais "Friction Trop Haute" (Zone d'échec). C'est pour lui montrer graphiquement pourquoi il échoue.

    --- FORMAT JSON STRICT ---
    {{
        "archetype": "STRING (Code MBTI - Nom)",
        "rarity": "STRING (Trait Dominant 1 / Trait Dominant 2)",
        "superpower": "STRING",
        "kryptonite": "STRING",
        "teaser_html": "STRING HTML (Long, formaté avec <p> et <strong>, coupé net...)",
        
        "preview_day": [
            {{ 
                "time": "HH:MM", 
                "phase": "NOM_PHASE", 
                "tag_visible": "COURT TAG (ex: Impact 80/20)", 
                "neuro_logic": "EXPLICATION FLOUTÉE (Pourquoi ce créneau ?)" 
            }},
            {{ 
                "time": "HH:MM", 
                "phase": "NOM_PHASE", 
                "tag_visible": "...", 
                "neuro_logic": "..." 
            }}
        ],
        
        "chart_energy": [ {{ "heure": "06", "niveau": 20 }}, {{ "heure": "08", "niveau": 50 }} ],
        "chart_matrix": [ {{ "tache": "Nom Tache", "impact": 90, "effort": 20 }} ],
        "chart_fogg": [ {{ "tache": "Projet Rêve", "friction": 80, "dopamine": 90, "zone": "Echec", "importance": 10 }} ]
    }}
    """


# --- ORCHESTRATEUR SÉCURISÉ ---
def parse_schedule(inputs):
    # On n'appelle plus qu'un seul prompt, court et rapide.
    prompt = _get_teaser_prompt(inputs)
    try:
        response = model.generate_content(prompt)
        return clean_and_parse_json(response.text) # On utilise toujours le nettoyeur !
    except Exception as e:
        print(f"Erreur Gemini: {e}")
        return None

def generate_ics_file(json_data):
    c = Calendar()
    data = json_data if isinstance(json_data, dict) else json.loads(json_data)
    start_date_ref = datetime.date.today() + datetime.timedelta(days=1)
    days = data.get("week_planning", [])
    for i, day in enumerate(days):
        current_date_str = (start_date_ref + datetime.timedelta(days=i)).isoformat()
        for task in day.get("tasks", []):
            try:
                e = Event()
                e.name = f"[{task.get('cat', 'FOCUS')}] {task.get('title')}"
                e.begin = f"{current_date_str}T{task.get('start')}:00"
                e.end = f"{current_date_str}T{task.get('end')}:00"
                c.events.add(e)
            except: continue
    return c.serialize()

def save_lead_to_gsheet(email, json_result_str, inputs):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        creds = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"],scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open("ChaosManager_Leads").sheet1
        sheet.append_row([str(datetime.datetime.now()), email, inputs['context'].get('status'), inputs['work_style'].get('chronotype'), "Lead V2", json_result_str])
    except Exception as e:
        print(f"⚠️ ERREUR CRITIQUE GSHEET : {e}") # Ça s'affichera dans tes logs Streamlit Cloud
        # pass # On garde le silence pour l'utilisateur, mais on crie dans les logs