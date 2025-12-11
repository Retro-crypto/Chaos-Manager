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

DEBUG_MODE = True 

def clean_and_parse_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match: cleaned_text = match.group(0)
    else: return {"error": "Pas de JSON trouvé"}
    try: return json.loads(cleaned_text)
    except:
        try: return ast.literal_eval(cleaned_text)
        except: return {"error": "Échec lecture JSON"}

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
    return json.dumps({"error": "Mode réel désactivé"})

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