import streamlit as st

st.title("🕵️‍♂️ Espion des Secrets")

st.write("Voici TOUT ce que je vois dans secrets.toml :")
st.write(st.secrets)

try:
    test = st.secrets["general"]["GEMINI_API_KEY"]
    st.success(f"✅ J'ai trouvé la clé ! Elle commence par : {test[:5]}...")
except KeyError:
    st.error("❌ La section [general] n'existe pas !")
except Exception as e:
    st.error(f"❌ Autre erreur : {e}")