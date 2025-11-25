import streamlit as st
from textblob import TextBlob
import matplotlib.pyplot as plt
from collections import Counter
import json
import base64

# === CONFIGURATION ===
CHROMEDRIVER_PATH = "C:/Users/bmd tech/Promobile/chromedriver-win64/chromedriver-win64/chromedriver.exe"
USER_DATA_DIR = "C:/Users/bmd tech/AppData/Local/Google/Chrome/User Data/Profile 1"
PROFILE_NAME = "merveille"

#URL_POST_FACEBOOK = "https://www.facebook.com/PromobileSenegal?locale=fr_FR"
st.set_page_config(page_title="Analyse Promobile", layout="centered")
st.title("📱 Analyse des commentaires Facebook Promobile")

# Chargement du fichier JSON
try:
    with open("resultats.json", "r", encoding="utf-8") as f:
        commentaires = json.load(f)
except FileNotFoundError:
    st.warning("🟡 Aucun commentaire trouvé. Lance d'abord `scraper.py` pour les récupérer.")
    st.stop()

# Analyse des sentiments
def analyser_sentiment(commentaire):
    score = TextBlob(commentaire).sentiment.polarity
    if score > 0.1:
        return "Positif"
    elif score < -0.1:
        return "Négatif"
    else:
        return "Neutre"

sentiments = [analyser_sentiment(c) for c in commentaires]

# Affichage des commentaires
st.subheader("📝 Commentaires analysés :")
for i, (c, s) in enumerate(zip(commentaires, sentiments), 1):
    st.markdown(f"{i}. **{s}** — _{c}_")

# Graphique circulaire
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
