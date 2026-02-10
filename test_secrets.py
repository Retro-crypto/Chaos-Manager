import streamlit as st
import os

st.title("🕵️‍♂️ Enquêteur de Secrets")

# 1. Vérifier où on est
st.write(f"📂 Dossier actuel : `{os.getcwd()}`")

# 2. Vérifier si le fichier existe
path = ".streamlit/secrets.toml"
if os.path.exists(path):
    st.success(f"✅ Le fichier '{path}' existe !")
else:
    st.error(f"❌ Le fichier '{path}' est INTROUVABLE.")

# 3. Essayer de lire le contenu
try:
    st.write("🔑 Contenu brut des secrets :")
    st.json(st.secrets)
except Exception as e:
    st.error(f"Erreur de lecture : {e}")