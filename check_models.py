import google.generativeai as genai
import os
from dotenv import load_dotenv

# Charger la clé
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERREUR : Clé API non trouvée dans le fichier .env")
else:
    print(f"Clé trouvée : {api_key[:5]}... (masquée)")
    try:
        genai.configure(api_key=api_key)
        print("\n--- MODÈLES DISPONIBLES ---")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
    except Exception as e:
        print(f"\nERREUR CRITIQUE : {e}")