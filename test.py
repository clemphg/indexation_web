import urllib.request
from bs4 import BeautifulSoup
import time

# Fonction pour télécharger une page et extraire les liens
def crawl_page(url):
    # Télécharger la page
    with urllib.request.urlopen(url) as response:
        html = response.read()

    # Analyser le contenu HTML
    soup = BeautifulSoup(html, 'html.parser')

    # Extraire les liens de la page
    links = [a['href'] for a in soup.find_all('a', href=True)]

    return links

# Fonction pour écrire les URLs dans le fichier crawled_webpages.txt
def write_to_file(urls):
    with open('crawled_webpages.txt', 'a') as file:
        for url in urls:
            file.write(url + '\n')

# Fonction principale du crawler
def main(start_url):
    # Liste des URLs à explorer
    to_crawl = [start_url]

    # Liste des URLs déjà explorées
    crawled = set()

    # Nombre maximum d'URLs à explorer
    max_urls = 50

    # Boucle principale du crawler
    while to_crawl and len(crawled) < max_urls:
        current_url = to_crawl.pop(0)

        # Vérifier si l'URL a déjà été explorée
        if current_url in crawled:
            continue

        # Télécharger la page et extraire les liens
        links = crawl_page(current_url)

        # Ajouter les nouveaux liens à la liste des URLs à explorer
        to_crawl.extend(links)

        # Ajouter l'URL actuelle à la liste des URLs explorées
        crawled.add(current_url)

        # Écrire les URLs dans le fichier crawled_webpages.txt
        write_to_file([current_url])

        # Respecter la politeness en attendant 3 secondes entre chaque appel
        time.sleep(3)

    print(f"Exploration terminée. {len(crawled)} URLs trouvées.")

# Point d'entrée du programme
if __name__ == "__main__":
    start_url = "https://ensai.fr/"
    main(start_url)
