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
        # --- MODE SIMULATION (DEBUG) ---
    if DEBUG_MODE:
        time.sleep(1.0) # Simulation calcul
        
        # Récupération des données riches pour personnaliser (fictif)
        work_style = inputs.get("work_style", {})
        animal = work_style.get("chronotype", "Ours").split(" ")[1] 
        
        # --- GENERATION DES DONNEES FICTIVES POUR LES GRAPHIQUES ---
        # 1. Courbe d'énergie (06h - 23h)
        energy_curve = []
        for h in range(6, 24):
            # Simulation d'un pic le matin et un creux l'aprem
            level = 50 + 40 * 0.9 if (9 <= h <= 12) else 30
            if h == 14: level = 20 # Crash digestion
            if h == 19: level = 70 # Rebond
            energy_curve.append({"heure": h, "niveau": int(level + random.randint(-5, 5))})

        # 2. Matrice Sociale
        matrix_data = [
            {"tache": "Réunion Client", "impact": -85},
            {"tache": "Brainstorming Équipe", "impact": -40},
            {"tache": "Code Solo (Python)", "impact": 90},
            {"tache": "Lecture Doc", "impact": 30},
            {"tache": "Emails", "impact": -10}
        ]
        fogg_data = [
            {"tache": "Code Python", "dopamine": 80, "friction": 40, "importance": 90, "zone": "Action", "description": "Grosse satisfaction, démarrage moyen."},
            {"tache": "Appeler Maman", "dopamine": 50, "friction": 20, "importance": 60, "zone": "Action", "description": "Facile et gratifiant."},
            {"tache": "Factures / Admin", "dopamine": 10, "friction": 90, "importance": 80, "zone": "Procrastination", "description": "L'enfer. Stratégie : Réduire la friction."},
            {"tache": "TikTok / Insta", "dopamine": 70, "friction": 5, "importance": 10, "zone": "Piège", "description": "Récompense immédiate, effort nul."}
        ]
        return json.dumps({
            # --- TEXTES D'ANALYSE ---
            "rarity": "Profil Neuro-Cross RARE",
            "archetype": f"{animal} Stratège", 
            "superpower": "Hyperfocus Séquentiel",
            "kryptonite": "Interruptions synchrones",
            "quote": "Le chaos n'est pas un ennemi, c'est du carburant mal raffiné.",
            
            "analysis_global": "Votre profil indique une haute tolérance au risque (O+) mais une batterie sociale faible (E-). L'IA a structuré la journée pour protéger vos blocs de concentration le matin.",
            "analysis_bio": "Pic de cortisol détecté à 08h30. Le créneau 09h-11h est mathématiquement votre fenêtre de rentabilité maximale.",
            "analysis_social": "Votre score d'Extraversion (E<30) transforme les réunions en dette énergétique. Le planning limite les interactions à 45min max.",
            "analysis_fogg": "Votre tâche 'Factures' est dans la zone critique (Friction > Motivation). Stratégie : Faites-le en 5min chrono (Micro-Sprint) pour baisser la friction.",
            # --- DONNÉES GRAPHIQUES ---
            "chart_energy": energy_curve,
            "chart_matrix": matrix_data,
            "chart_fogg": fogg_data,

            # --- PLANNING ---
            "planning": [
                { "titre": "🌞 Activation Dopaminergique", "start_iso": "2025-12-12T07:30:00", "end_iso": "2025-12-12T08:00:00", "categorie": "Santé", "description": "Lumière directe + Protéines. Pas de téléphone." },
                { "titre": "🧠 Deep Work (Pic Cortisol)", "start_iso": "2025-12-12T09:00:00", "end_iso": "2025-12-12T11:30:00", "categorie": "Travail", "description": "Tâche unique : Avancer sur le projet Python." },
                { "titre": "⚡ Admin Burst (Basse énergie)", "start_iso": "2025-12-12T13:30:00", "end_iso": "2025-12-12T14:30:00", "categorie": "Admin", "description": "Emails, appels, factures. Mode robot." },
                { "titre": "🔄 Reset Cognitif", "start_iso": "2025-12-12T16:00:00", "end_iso": "2025-12-12T16:20:00", "categorie": "Santé", "description": "NSDR ou Marche rapide." },
                { "titre": "🎨 Creative Flow (Loup)", "start_iso": "2025-12-12T20:00:00", "end_iso": "2025-12-12T22:00:00", "categorie": "Créativité", "description": "Pas de censure, écriture libre." }
            ]
        })

    # --- MODE RÉEL (Génératif) ---
    # Ici tu mettras ton appel Gemini plus tard
    else: 
        today_date = datetime.date.today().isoformat()
        """
        Le Cerveau Principal.
        Reçoit : Dictionnaire 'inputs' (Scores, Routine, Mission, etc.)
        Renvoie : String JSON complet pour le Frontend.
        """
        
        # 1. Extraction des données pour le Prompt
        scores = inputs.get("scores", {})
        work_style = inputs.get("work_style", {})
        context = inputs.get("context", {})
        
        # 2. Construction du Mega-Prompt (Ingénierie de Prompt)
        user_prompt = f"""
        CONTEXTE UTILISATEUR (NEURO-PROFIL):
        - Scores OCEAN : {scores}
        - Chronotype (Energie) : {work_style.get('chronotype')}
        - Tendance Discipline (Rubin) : {work_style.get('tendency')}
        - Zone de Génie (Lencioni) : {work_style.get('genius')}
        
        CONTEXTE OPERATIONNEL :
        - Routine Actuelle : "{context.get('routine')}"
        - Blocages / Freins identifiés : "{context.get('blockers')}"
        - MISSION DU JOUR (Impératifs) : "{context.get('mission')}"

        TACHE :
        Agis comme un architecte de systèmes cognitifs expert.
        1. Analyse les failles entre le profil de l'utilisateur et sa routine actuelle.
        2. Génère un planning ultra-optimisé qui respecte sa biologie (Chronotype) et sa psychologie.
        3. Calcule les données pour les graphiques d'énergie, de matrice sociale et de modèle Fogg.
        
        CONTRAINTES DE SORTIE (JSON STRICT) :
        Tu DOIS répondre UNIQUEMENT par un objet JSON respectant exactement cette structure :
        {{
            "rarity": "Nom RPG du profil (ex: Archimage Chaotique)",
            "archetype": "Titre Professionnel (ex: Stratège Nocturne)",
            "quote": "Citation courte percutante adaptée au profil",
            "superpower": "Le plus grand atout cognitif de ce profil",
            "kryptonite": "La plus grande faiblesse (ex: Ennui administratif)",
            
            "analysis_global": "Analyse psycho-stratégique (3 phrases max). Explique pourquoi tu as structuré la journée ainsi.",
            "analysis_bio": "Analyse du rythme circadien spécifique à ce profil.",
            "analysis_social": "Analyse du coût énergétique social (Introversion/Extraversion).",
            "analysis_fogg": "Analyse comportementale (Dopamine vs Friction) basée sur les 'Blockers' fournis.",
            
            "chart_energy": [
                {{"heure": 6, "niveau": 20}}, ... jusqu'à 23h. (0-100)
            ],
            "chart_matrix": [
                {{"tache": "Nom Tache", "impact": -50}} (Impact négatif = Drain, Positif = Recharge)
            ],
            "chart_fogg": [
                {{"tache": "Nom Tache", "dopamine": 10-100, "friction": 10-100, "importance": 10-100, "zone": "Action/Procrastination/Piège", "description": "Court commentaire"}}
            ],
            
            "planning": [
                {{
                    "titre": "Titre Action",
                    "start_iso": "YYYY-MM-DDTHH:MM:00", (Date de demain par défaut)
                    "end_iso": "YYYY-MM-DDTHH:MM:00",
                    "categorie": "Travail/Santé/Admin/DeepWork",
                    "description": "Consigne tactique précise (ex: 'Téléphone dans l'autre pièce')"
                }}
            ]
        }}
        """

        try:
            # 3. Appel à Gemini (Le "vrai" traitement)
            response = model.generate_content(user_prompt)
            
            # 4. Nettoyage et Renvoi
            json_data = clean_and_parse_json(response.text)
            
            # Petit hack pour s'assurer que les dates du planning sont valides (parfois l'IA met des dates fictives)
            # On pourrait ajouter ici une logique pour recaler les dates sur "Aujourd'hui" ou "Demain"
            
            return json.dumps(json_data)

        except Exception as e:
            return json.dumps({
                "error": f"Erreur Gemini : {str(e)}",
                "planning": [],
                "analysis_global": "L'IA n'a pas pu traiter la demande. Vérifiez votre clé API ou vos quotas."
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