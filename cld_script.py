import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from datetime import datetime, timedelta
import time
import re

# Pour l'analyse de sentiment
from textblob import TextBlob
import nltk
# nltk.download('punkt') # À exécuter une seule fois

class PromobileScraper:
    def __init__(self):
        """Initialise le scraper avec configuration Chrome"""
        self.chrome_options = Options()
        # Configuration Chrome optimisée
        self.chrome_options.add_argument("--headless")  # Mode sans interface
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-gpu")
        
        # Optimisation mémoire - IMPORTANT pour éviter les crashes
        self.chrome_options.add_argument("--memory-pressure-off")
        self.chrome_options.add_argument("--max_old_space_size=4096")
        self.chrome_options.add_argument("--disable-background-timer-throttling")
        self.chrome_options.add_argument("--disable-renderer-backgrounding")
        
        # Désactiver les fonctionnalités inutiles
        self.chrome_options.add_argument("--disable-web-security")
        self.chrome_options.add_argument("--disable-features=TranslateUI")
        self.chrome_options.add_argument("--disable-iframes")
        self.chrome_options.add_argument("--disable-plugins")
        
        # Bloquer WebRTC (cause des erreurs STUN)
        self.chrome_options.add_argument("--disable-webrtc")
        
        self.chrome_options.add_argument("--window-size=1280,720")  # Résolution plus petite
        # User-agent pour éviter la détection
        self.chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        self.driver = None
        self.comments_data = []
    
    def init_driver(self):
        """Initialise le driver Chrome"""
        try:
            self.driver = webdriver.Chrome(options=self.chrome_options)
            self.driver.implicitly_wait(10)
            return True
        except Exception as e:
            print(f"Erreur lors de l'initialisation du driver : {e}")
            return False
    
    def analyze_sentiment(self, text):
        """Analyse le sentiment d'un texte"""
        try:
            # Nettoie le texte
            clean_text = re.sub(r'[^\w\s]', '', text.lower())
            
            # Utilise TextBlob pour l'analyse
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            # Classifie le sentiment
            if polarity > 0.1:
                return "Positif"
            elif polarity < -0.1:
                return "Négatif"
            else:
                return "Neutre"
        except:
            return "Neutre"
    
    def scrape_facebook_comments(self, url, days_limit=30):
        """Scrape les commentaires Facebook (version basique)"""
        print("🔍 Scraping Facebook...")
        
        if not self.init_driver():
            return []
        
        comments = []
        
        try:
            # Charger la page
            print("   📱 Chargement de la page Facebook...")
            self.driver.get(url)
            time.sleep(8)  # Attendre plus longtemps
            
            print("   🔍 Recherche des éléments...")
            
            # Essayer plusieurs sélecteurs possibles pour Facebook
            selectors_to_try = [
                '[data-pagelet="FeedUnit"]',
                '.userContentWrapper',
                '[data-testid="story-subtitle"]',
                '.story_body_container',
                '._5pbx'
            ]
            
            posts_found = False
            for selector in selectors_to_try:
                try:
                    posts = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if posts:
                        print(f"   ✅ Trouvé {len(posts)} éléments avec le sélecteur: {selector}")
                        posts_found = True
                        break
                except Exception as e:
                    print(f"   ⚠️  Sélecteur {selector} échoué: {e}")
                    continue
            
            if not posts_found:
                print("   ❌ Aucun post trouvé, essai d'une approche différente...")
                # Essayer de récupérer tout le texte visible
                page_text = self.driver.find_element(By.TAG_NAME, "body").text
                if "promobile" in page_text.lower() or len(page_text) > 100:
                    print("   📝 Contenu de page détecté, création d'un exemple...")
                    comments.append({
                        'plateforme': 'Facebook',
                        'type': 'Page_Content',
                        'contenu': page_text[:200] + "...",
                        'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                        'sentiment': self.analyze_sentiment(page_text[:200])
                    })
            else:
                # Traiter les posts trouvés
                for i, post in enumerate(posts[:3]):
                    try:
                        text_content = post.text
                        if text_content and len(text_content) > 10:
                            comment_data = {
                                'plateforme': 'Facebook',
                                'type': 'Post',
                                'contenu': text_content[:300],  # Limiter la taille
                                'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                                'sentiment': self.analyze_sentiment(text_content)
                            }
                            comments.append(comment_data)
                            print(f"   ✅ Post {i+1} récupéré: {text_content[:50]}...")
                    
                    except Exception as e:
                        print(f"   ⚠️  Erreur post {i}: {e}")
                        continue
                        
        except Exception as e:
            print(f"   ❌ Erreur Facebook : {e}")
            
            # Mode de récupération d'urgence
            try:
                print("   🚨 Mode de récupération...")
                page_source = self.driver.page_source[:1000]
                if page_source:
                    comments.append({
                        'plateforme': 'Facebook',
                        'type': 'Debug_Content',
                        'contenu': f"Page source disponible: {len(self.driver.page_source)} caractères",
                        'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                        'sentiment': 'Neutre'
                    })
            except:
                pass
        
        finally:
            if self.driver:
                self.driver.quit()
        
        return comments
    
    def scrape_linkedin_posts(self, url, days_limit=30):
        """Scrape les posts LinkedIn (version basique)"""
        print("🔍 Scraping LinkedIn...")
        
        if not self.init_driver():
            return []
        
        posts = []
        
        try:
            self.driver.get(url)
            time.sleep(5)
            
            # LinkedIn nécessite souvent une connexion
            # Pour ce test, on essaie de récupérer ce qui est visible
            
            post_elements = self.driver.find_elements(By.CSS_SELECTOR, ".feed-shared-update-v2")
            
            for i, post in enumerate(post_elements[:3]):  # Limite à 3 posts pour test
                try:
                    # Récupérer le contenu du post
                    content_elem = post.find_element(By.CSS_SELECTOR, ".feed-shared-text")
                    post_text = content_elem.text
                    
                    if post_text:
                        post_data = {
                            'plateforme': 'LinkedIn',
                            'type': 'Post',
                            'contenu': post_text,
                            'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                            'sentiment': self.analyze_sentiment(post_text)
                        }
                        posts.append(post_data)
                        print(f"✅ Post LinkedIn récupéré : {post_text[:50]}...")
                
                except Exception as e:
                    print(f"Erreur post LinkedIn {i}: {e}")
                    continue
        
        except Exception as e:
            print(f"Erreur LinkedIn : {e}")
        
        finally:
            if self.driver:
                self.driver.quit()
        
        return posts
    
    def get_all_comments(self):
        """Récupère tous les commentaires des deux plateformes"""
        print("🚀 Début du scraping...")
        
        # URLs des pages Promobile
        facebook_url = "https://www.facebook.com/PromobileSenegal?locale=fr_FR"
        linkedin_url = "https://www.linkedin.com/company/promobilesn/posts/?feedView=all"
        
        all_data = []
        
        # Scraping Facebook
        fb_data = self.scrape_facebook_comments(facebook_url)
        all_data.extend(fb_data)
        
        # Pause entre les scraping
        time.sleep(3)
        
        # Scraping LinkedIn
        li_data = self.scrape_linkedin_posts(linkedin_url)
        all_data.extend(li_data)
        
        return all_data
    
    def analyze_results(self, data):
        """Analyse les résultats obtenus"""
        if not data:
            print("❌ Aucune donnée récupérée")
            return
        
        df = pd.DataFrame(data)
        
        print(f"\n📊 RÉSULTATS DE L'ANALYSE")
        print(f"Total des éléments analysés : {len(df)}")
        print(f"\n--- Par plateforme ---")
        print(df['plateforme'].value_counts())
        print(f"\n--- Par sentiment ---")
        print(df['sentiment'].value_counts())
        
        # Afficher quelques exemples
        print(f"\n--- Exemples de contenu ---")
        for i, row in df.head(3).iterrows():
            print(f"\n{row['plateforme']} - {row['sentiment']}")
            print(f"Contenu: {row['contenu'][:100]}...")
        
        return df


def main():
    """Fonction principale pour tester le scraper"""
    print("🔧 PROMOBILE SCRAPER - VERSION TEST")
    print("=" * 50)
    
    scraper = PromobileScraper()
    
    # Récupération des données
    data = scraper.get_all_comments()
    
    # Analyse des résultats
    results_df = scraper.analyze_results(data)
    
    # Sauvegarde optionnelle (pour debug)
    if data:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"promobile_data_{timestamp}.csv"
        pd.DataFrame(data).to_csv(filename, index=False, encoding='utf-8')
        print(f"\n💾 Données sauvegardées dans : {filename}")


if __name__ == "__main__":
    main()