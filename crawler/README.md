# TP d'indexation web [Crawler] - ENSAI 2024
Clémentine Phung [clementine.phung-ngoc@eleve.ensai.fr]

Ce `README.md` correspond au TP1 sur les crawlers.

## Généralités

Ce projet présente deux implémentation de crawlers. Le premier a les propriétés de base demandées, et le second présente quelques éléments bonus, tel que la lecture du fichier `sitemap.xml` des sites.

Les deux crawlers permettent d'explorer des pages à partir d'une URL d'entrée unique, ici https://ensai.fr/. Ils offrent la possibilité de s'arrêter à l'exploration d'un certain nombre (défini au préalable) de liens par pages. De façon similaire, ils s'arrêtent lorsqu'ils ont trouvé et téléchargé un certain nombre d'URLs ou lorsqu'ils ne trouvent plus de liens à explorer.

Chaque crawler attend cinq secondes entre chaque téléchargement de page. Ils consultent aussi les fichiers `robots.txt` des sites afin de ne crawler que les pages qu'ils sont autorisés à crawler. Enfin, ils respectent la politesse en attendant trois secondes avant chaque interrogation d'un fichier `robots.txt`.

## Implémentation

J'ai choisi de modéliser un crawler par une classe. Ainsi toutes les méthodes et les attributs correspondant au crawler sont encapsulés dans l'objet. Le crawler minimal est l'objet `MinimalCrawler` et l'autre est l'objet `Crawler`.

### Principales librairies utilisées

- **urllib** pour requêter les urls et lire les `robots.txt`.
- **beautifulsoup4** pour lire les fichiers html.
- **sqlite3** pour la base de données.

### Objet `MinimalCrawler`

Ce crawler correspond au crawler minimal demandé. Il est single-threaded, ce qui signifie que toutes les opérations sont réalisées séquentiellement.

### Constructeur

Cet objet `MinimalCrawler` initialise six attributs lors de son instanciation. Ils sont définis tel que suit :
```python
class MinimalCrawler():
def __init__(self,
             start_url:str, 
             max_urls_crawled:int=50, 
             max_urls_per_page:int=5,
             crawl_delay:int=5, 
             robot_delay:int=3,
             timeout_delay:int=5) -> None:

        self.__seed = start_url

        self.__max_urls_crawled = max_urls_crawled
        self.__max_urls_per_page = max_urls_per_page

        self.__crawl_delay = crawl_delay  # seconds
        self.__robot_delay = robot_delay  # seconds
        self.__timeout_delay = timeout_delay # seconds
```
Le seul n'ayant pas de valeur par défaut est l'attribut `seed`, qui correspond à l'URL de départ pour crawler, ici https://ensai.fr. Les autres prennent par défaut la valeur spécifiée dans l'énoncé:

- `__max_urls_crawled = 50` : le crawler s'arrête après avoir exploré cinquante pages,
- `__max_urls_per_page = 5` : le crawler se limite à l'exploration d'au maximum cinq liens sortant par page,
- `__crawl_delay = 5` : le crawler attend cinq secondes avant de crawler la page suivante,
- `__robot_delay = 3` : le crawler attend trois secondes avant d'interroger à nouveau un `robots.txt`.

Finalement, `__timeout_delay` est utilisé pour éviter de perdre trop de temps sur une URL que le crawler aurait des difficultés à atteindre.

### Méthodes

Après le constructeur, ce crawler a quatre méthodes, trois privées et une publique. Les méthodes sont les suivantes :

- `__write_visited_urls(self, urls:list[str], path:str, filename:str) -> None` : écrit une liste d'URLs dans un fichier dans un dossier spécifié.
- `__scan_links_in_page(self, page_url:str) -> (bool, list[str]):` : parse l'HTML de la page et extrait des liens vers des pages pouvant elles-mêmes être parsées.
- `__is_crawlable(self, page_url:str) -> bool` : vérifie s'il est possible de parser une page suivant les règles du fichier `robots.txt`.
- `crawl(self, filename:str, path:str) -> None` : crawl complet, appelle les autres méthodes et s'arrête quand un certain nombre de liens ont été visités ou lorsque la frontière est vide.

### Objet `Crawler`

### Constructeur

`Crawler` a les mêmes 6 attributs que `MinimalCrawler`. 

### Méthodes

Ce crawler a les mêmes méthodes que le crawler minimal et des méthodes supplémentaires qui permettent la lecture des **sitemaps** des sites web ainsi que la sauvegarde des URLs avec leur âge dans une **base de données**. Les méthodes communes aux deux crawlers peuvent légèrement différer.  

- `__write_visited_urls(self, urls:list[str], path:str, filename:str) -> None` : écrit une liste d'URLs dans un fichier dans un dossier spécifié.
- `__scan_links_in_page(self, page_url:str) -> (bool, list[str])` : parse l'HTML de la page accessible depuis l'URL et extrait les liens sortant de la page.
- `__is_crawlable(self, page_url:str) -> bool` : vérifie s'il est possible de parser une page suivant les règles du fichier `robots.txt`.
- `__get_sitemaps(self, url:str) -> (list[str]|None)` : retourne la liste des sitemaps du site web s'il y en a, `None` sinon.
- `__scan_sitemap(self, sitemap:str) -> list[str]` : parse une sitemap, extrait tous les liens sortants et vérifie s'ils peuvent être crawlés suivant les règles du fichier `robots.txt`.
- `__scan_urls_from_sitemap(self, url:str) -> (bool, list[str])` : fait appel aux deux méthodes précédente et retourne toutes les URLs contenues dans toutes les sitemaps du site.
- `__get_links_one_page(self, url:str) -> (list[str]|None)` : joint les URLs trouvées sur la page qui est en train d'être crawlée et sur les sitemaps du site web (s'il y a lieu) puis retourne une liste d'un certain nombre (selon paramètre, par défaut 5) d'entre elles qui peuvent être crawlées suivant les règles des fichiers `robots.txt`.
- `__db_create_table(self, tablename:str, dbname:str, path:str) -> str` : crée une base de données si elle n'existe pas déjà puis crée une table (url, age) et retourne le nom de la table créée.
- `__db_add_url(self, url:str, tablename:str, dbname:str, path:str) -> None` : ajoute une URL à la base de données, renseigne son âge à 0 puis incrémente l'âge des autres URLs d'1.
- `crawl(self, filename:str, dbname:str, tablename:str, path:str) -> None` :  crawl complet, appelle les autres méthodes et s'arrête quand un certain nombre de liens ont été visités ou lorsque la frontière est vide.

## Utilisation

Pour utiliser le crawler avec les options décrite dans cette section, veuillez vous placer dans le dossier `/crawler`. 

Pour utiliser le crawler avec les options par défaut, entrer 
```
python3 main.py
```
Le crawler plus développé avec la lecture des **sitemaps** et la sauvegarde de l'âge dans une **base de données** sera alors utilisé.

Le crawler dans la version de base demandée peut être utilisé avec la ligne suivante :
```
python3 main.py -c minimal
```

La documentation complète des options disponibles pour le crawler et le crawl est accessible avec
```
python3 main.py --help
```
```
usage: main.py [-h] [-s SEED] [-mc MAX_URLS_TO_CRAWL] [-mp MAX_URLS_PER_PAGE] [-cd CRAWL_DELAY] [-rd ROBOT_DELAY] [-td TIMEOUT_DELAY] [-p PATH] [-f FILENAME] [-db DBNAME] [-t TABLENAME]
               [-c {minimal,normal}]

options:
  -h, --help            show this help message and exit
  -s SEED, --seed SEED  Start URL for crawler, default 'https://ensai.fr'.
  -mc MAX_URLS_TO_CRAWL, --max_urls_to_crawl MAX_URLS_TO_CRAWL
                        Maximum number of webpages to crawl, default 50.
  -mp MAX_URLS_PER_PAGE, --max_urls_per_page MAX_URLS_PER_PAGE
                        Maximum number of links to keep for each crawled webpage, default 5.
  -cd CRAWL_DELAY, --crawl_delay CRAWL_DELAY
                        Delay between each page crawl, in seconds, default 5.
  -rd ROBOT_DELAY, --robot_delay ROBOT_DELAY
                        Politeness for robots.txt file access, in seconds, default 3.
  -td TIMEOUT_DELAY, --timeout_delay TIMEOUT_DELAY
                        Timeout for urllib.requests.urlopen, in seconds, default 5.
  -p PATH, --path PATH  Path to save results to, default '.'
  -f FILENAME, --filename FILENAME
                        Filename to save crawled webpages URLs, default 'crawled_webpages.txt'.
  -db DBNAME, --dbname DBNAME
                        Database name in which crawled webpages URLs and their age are saved, default 'crawled_webpages.db'.
  -t TABLENAME, --tablename TABLENAME
                        Name of table in which crawled webpages URLs and their age are saved, default 'webpages_age'.
  -c {minimal,normal}, --crawler {minimal,normal}
                        Crawler to use, default 'normal'.
```
Les options non disponibles pour le crawler minimal ne seront pas utilisées même si elles sont renseignées. Celles-ci sont les options relatives à la base de données, soit `--dbname` et `--tablename`.
