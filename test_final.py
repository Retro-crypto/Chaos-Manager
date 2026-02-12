import streamlit as st
import google.generativeai as genai
import os

st.title("🚑 Urgences Réanimation")

# 1. Vérif des Secrets
st.subheader("1. Lecture des Secrets")
try:
    api_key = st.secrets["general"]["GEMINI_API_KEY"]
    st.success(f"✅ Clé récupérée (Début : {api_key[:5]}...)")
except Exception as e:
    st.error(f"❌ Erreur de lecture secrets.toml : {e}")
    st.stop()

# 2. Vérif de Gemini
st.subheader("2. Test de Connexion Gemini")
try:
    genai.configure(api_key=api_key)
    # On utilise un modèle basique pour tester
    model = genai.GenerativeModel("gemini-2.5-flash") 
    response = model.generate_content("Réponds juste 'OK' si tu me reçois.")
    
    st.success(f"✅ RÉPONSE REÇUE : {response.text}")
    st.balloons()
    
except Exception as e:
    st.error("💀 ERREUR CRITIQUE GEMINI :")
    st.code(str(e)) # Affiche le message technique exact