from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import json

CHROMEDRIVER_PATH = "C:/Users/bmd tech/Promobile/chromedriver-win64/chromedriver-win64/chromedriver.exe"
USER_DATA_DIR = "C:/Users/bmd tech/AppData/Local/Google/Chrome/User Data/Profile 1"
PROFILE_NAME = "merveille"
URL = "https://www.facebook.com/Congolaistv.officiel" # ton lien réel ici

options = Options()
options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
options.add_argument(f"--profile-directory={PROFILE_NAME}")
options.add_argument("--start-maximized")

driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=options)
driver.get(URL)

input("➡️ Connecte-toi, affiche bien les commentaires visibles, puis appuie sur Entrée ici pour lancer l’extraction...")

def scroller(driver, secondes=2, repetitions=5):
    for _ in range(repetitions):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(secondes)

def expand_all_comments(driver):
    try:
        boutons = driver.find_elements(By.XPATH, "//div[@role='button' and contains(., 'Voir plus de commentaires')]")
        for bouton in boutons:
            try:
                driver.execute_script("arguments[0].click();", bouton)
                time.sleep(1)
            except:
                continue
    except:
        pass

def extraire_commentaires(driver):
    commentaires = []
    elements = driver.find_elements(By.XPATH, "//div[@role='article']//div[contains(@dir, 'auto')]")
    for el in elements:
        texte = el.text.strip()
        if texte and len(texte.split()) > 2:
            commentaires.append(texte)
    return list(set(commentaires))

expand_all_comments(driver)
scroller(driver)
commentaires = extraire_commentaires(driver)
driver.quit()

# Sauvegarde dans un fichier JSON
with open("file_j.json", "w", encoding="utf-8") as f:
    json.dump(commentaires, f, ensure_ascii=False, indent=2)

print(f"✅ {len(commentaires)} commentaires sauvegardés dans resultats.json")
