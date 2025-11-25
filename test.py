from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

# Remplace par ton propre chemin vers ChromeDriver si besoin
CHROMEDRIVER_PATH = "C:/Users/bmd tech/Promobile/chromedriver-win64/chromedriver-win64/chromedriver.exe"

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-notifications")

driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=options)

# 1. Ouvrir Facebook + injecter les cookies
driver.get("https://www.facebook.com")
time.sleep(5)

cookies = [
    {"name": "c_user", "value": "61577905995067"},
    {"name": "xs", "value": "42%3ATVVBrGTZ_Nec3w%3A2%3A1752079065%3A-1%3A-1%3A%3AAcUrS70L5OqFg-JROK3KzZZU04COVVol_ol3wMKH7M0"},
    {"name": "datr", "value": "pNBUaDR2FyYBGFDZ4zRMVl_L"},
    {"name": "sb", "value": "pNBUaIPdkyE3dm1hgh8-jcRP"},
    {"name": "fr", "value": "1AxwbKTdGvu9itiZf.AWdlLjeEZlcrlDpkanpDnAzTQ"},
    {"name": "locale", "value": "fr_FR"},
    {"name": "presence", "value": "C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1752661905715%2C%22v%22%3A1%7D"}
]

for cookie in cookies:
    driver.add_cookie(cookie)

# 2. Aller à la page de Promobile
driver.get("https://www.facebook.com/PromobileSenegal?locale=fr_FR")
time.sleep(10)

# 3. Scroll profond pour charger le maximum de contenu
for _ in range(12):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

# 4. Cliquer sur tous les “Voir plus de commentaires”
voir_plus = driver.find_elements(By.XPATH, "//div[contains(text(),'voir plus de commentaires')]")
for bouton in voir_plus:
    try:
        driver.execute_script("arguments[0].click();", bouton)
        time.sleep(2)
    except:
        continue

# 5. Tenter de récupérer tous les commentaires visibles
comment_elements = driver.find_elements(By.XPATH, "//ul[contains(@aria-label, 'commentaires') or contains(@aria-label, 'Commentaires')]//div[@dir='auto']")

commentaires = []
for elt in comment_elements:
    texte = elt.text.strip()
    if texte and texte.lower() != "commenter" and len(texte) > 5:
        commentaires.append(texte)

# 6. Afficher les résultats
print("\n📌 Commentaires Facebook récupérés :\n")
for i, c in enumerate(commentaires[:30], 1):
    print(f"{i}. {c}\n")

input("Appuie sur Entrée pour quitter...")
driver.quit()
