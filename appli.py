import streamlit as st
import base64
import json
import matplotlib.pyplot as plt
from collections import Counter
from transformers import pipeline
from deep_translator import GoogleTranslator

# === CONFIG PAGE ===
st.set_page_config(page_title="Analyse Promobile", layout="centered")

# === IMAGE DE FOND ===
def add_bg_from_local(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
        }}
        .block-container {{
            background-color: rgba(255, 255, 255, 0.95);
            padding: 2rem 3rem;
            border-radius: 15px;
        }}
        h1, h2, h3, h4, p {{
            color: black !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

add_bg_from_local("promob.png")  # ← ton image locale

# === TITRE ===
st.title("📱 Analyse des commentaires Facebook Promobile")

# === CHARGEMENT DES COMMENTAIRES ===
try:
    with open("file_j.json", "r", encoding="utf-8") as f:
        commentaires = json.load(f)
except FileNotFoundError:
    st.warning("⚠️ Aucun commentaire trouvé. Lance d’abord `scraper.py`.")
    st.stop()

# === MODELE EN ANGLAIS (ultra compatible)
@st.cache_resource(show_spinner="Chargement du modèle anglais...")
def charger_pipeline():
    return pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

analyzer = charger_pipeline()

# === ANALYSE AVEC TRADUCTION
def analyser_sentiment(commentaire_fr):
    try:
        commentaire_en = GoogleTranslator(source='auto', target='en').translate(commentaire_fr)
        result = analyzer(commentaire_en[:512])[0]
        label = result["label"]
        if label == "POSITIVE":
            return "Positif"
        elif label == "NEGATIVE":
            return "Négatif"
        else:
            return "Neutre"
    except Exception as e:
        print("Erreur:", e)
        return "Neutre"

with st.spinner("🧠 Analyse des commentaires en cours..."):
    sentiments = [analyser_sentiment(c) for c in commentaires]

# === AFFICHAGE DES COMMENTAIRES
st.subheader("📝 Commentaires analysés")
for i, (c, s) in enumerate(zip(commentaires, sentiments), 1):
    st.markdown(f"{i}. **{s}** — _{c}_")

# === GRAPH CIRCULAIRE
st.subheader("📊 Répartition des sentiments")
compte = Counter(sentiments)

fig, ax = plt.subplots()
ax.pie(
    compte.values(),
    labels=compte.keys(),
    autopct='%1.1f%%',
    startangle=140,
    colors=['lightgreen', 'lightcoral', 'lightgray']
)
ax.axis('equal')
st.pyplot(fig)
