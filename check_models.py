import google.generativeai as genai
import os
from dotenv import load_dotenv

# Charge les variables d'environnement (ta clé dans .env)
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ ERREUR : Aucune clé API trouvée dans le fichier .env")
else:
    print(f"🔑 Clé trouvée : {api_key[:5]}...*****")
    
    try:
        genai.configure(api_key=api_key)
        print("📡 Tentative de connexion aux serveurs Google...")
        
        print("\n📋 LISTE DES MODÈLES DISPONIBLES POUR TOI :")
        print("-" * 40)
        
        found = False
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"✅ {m.name}")
                found = True
        
        if not found:
            print("❌ Aucun modèle compatible trouvé. Vérifie si ton compte a accès à l'API.")
        else:
            print("-" * 40)
            print("🚀 CONSEIL : Utilise le nom EXACT affiché ci-dessus dans ton backend.py")

    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE : {e}")