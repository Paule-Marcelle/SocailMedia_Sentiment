from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from transformers import pipeline
import time
import pandas as pd

def analyser_commentaires(commentaires):
    sentiment_pipeline = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")
    resultats = []
    for commentaire in commentaires:
        if commentaire.strip() != "":
            res = sentiment_pipeline(commentaire[:512])[0]
            resultats.append({
                "commentaire": commentaire,
                "label": res['label'],
                "score": round(res['score'], 2),
                "source": "LinkedIn"
            })
    return pd.DataFrame(resultats)

def scraper_linkedin():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get("https://www.linkedin.com/login")
    print("🟡 Connecte-toi à LinkedIn dans les 40 secondes...")
    time.sleep(40)

    driver.get("https://www.linkedin.com/company/promobilesn/posts/?feedView=all")
    print("🟢 Chargement des publications Promobile...")
    time.sleep(10)

    commentaires = []
    publications = driver.find_elements(By.CSS_SELECTOR, 'div.feed-shared-update-v2')

    for post in publications:
        try:
            try:
                bouton = post.find_element(By.XPATH, './/button[contains(text(), "commentaire")]')
                bouton.click()
                time.sleep(2)
            except:
                pass

            spans = post.find_elements(By.CSS_SELECTOR, 'span.comments-comment-item__main-content')
            for span in spans:
                txt = span.text.strip()
                if txt and len(txt) > 3:
                    commentaires.append(txt)

        except Exception as e:
            print("⚠️ Erreur sur un post :", e)

    driver.quit()

    print(f"✅ {len(commentaires)} commentaires récupérés.")
    df = analyser_commentaires(commentaires)
    print(df[["commentaire", "label", "score"]])
    return df
