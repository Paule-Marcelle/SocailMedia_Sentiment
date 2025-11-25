from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

CHROMEDRIVER_PATH = "C:/Users/bmd tech/Promobile/chromedriver-win64/chromedriver-win64/chromedriver.exe"  # adapte si besoin

# Setup
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-notifications")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/90.0.4430.212 Safari/537.36")

driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=options)

# Étape 1 : Aller une première fois sur LinkedIn
driver.get("https://www.linkedin.com")
time.sleep(5)

# Étape 2 : Injecter uniquement le cookie li_at
driver.add_cookie({
    "name": "li_at",
    "value": "AQEDAVxo3EsCn_kXAAABl9Trn84AAAGYHoY1Ik0AH",
    "domain": ".linkedin.com"
})

# Étape 3 : Aller sur la page des posts Promobile
driver.get("https://www.linkedin.com/company/promobilesn/posts/")
time.sleep(10)

# Étape 4 : Scroll profond pour charger les publications
for _ in range(8):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

# Étape 5 : Récupération des publications
posts = driver.find_elements(By.XPATH, "//div[contains(@data-urn, 'urn:li:activity')]")
print(f"🔍 {len(posts)} publications trouvées.")

commentaires = []

# Étape 6 : Parcours des publications
for idx, post in enumerate(posts[:5]):
    try:
        driver.execute_script("arguments[0].scrollIntoView(true);", post)
        time.sleep(2)

        # Cliquer sur “voir les commentaires” s’il existe
        try:
            bouton = post.find_element(By.XPATH, ".//button[contains(text(), 'commentaire')]")
            driver.execute_script("arguments[0].click();", bouton)
            time.sleep(3)
        except:
            pass

        # Extraire les commentaires visibles
        comment_elements = post.find_elements(By.XPATH, ".//span[@dir='ltr']")
        for elt in comment_elements:
            texte = elt.text.strip()
            if texte and len(texte) > 5:
                commentaires.append(texte)

    except Exception as e:
        print(f"❌ Erreur sur la publication {idx + 1}: {e}")
        continue

# Étape 7 : Affichage
print("\n📌 Commentaires LinkedIn récupérés :\n")
for i, c in enumerate(commentaires[:30], 1):
    print(f"{i}. {c}\n")

input("Appuie sur Entrée pour quitter...")
driver.quit()
