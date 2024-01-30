# TP d'indexation web [Crawler] - ENSAI 2024
Clémentine Phung [clementine.phung-ngoc@eleve.ensai.fr]

Ce `README.md` correspond au TP1 sur les crawlers.

## Généralités

Ce projet présente deux implémentation de crawlers. Le premier a les propriétés de base demandées, et le second présente quelques éléments bonus, tel que la lecture du fichier `sitemap.xml` des sites.

Les deux crawlers permettent d'explorer des pages à partir d'une URL d'entrée unique, ici https://ensai.fr/. Ils offrent la possibilité de s'arrêter à l'exploration d'un certain nombre (défini au préalable) de liens par pages. De façon similaire, ils s'arrêtent lorsqu'ils ont trouvé et téléchargé un certain nombre d'URLs ou lorsqu'ils ne trouvent plus de liens à explorer.

Chaque crawler attend cinq secondes entre chaque téléchargement de page. Ils consultent aussi les fichiers `robots.txt` des sites afin de ne crawler que les pages qu'ils sont autorisés à crawler. Enfin, ils respectent la politesse en attendant trois secondes avant chaque interrogation d'un fichier `robots.txt`.

## Implémentation

J'ai choisi de modéliser un crawler par une classe. Ainsi toutes les méthodes et les attributs correspondant au crawler sont encapsulés dans l'objet. Le crawler minimal est l'objet `MinimalCrawler` et l'autre est l'objet `Crawler`.

### Librairies utilisées

- **urllib** pour requêter les urls et lire les `robots.txt`.
- **beautifulsoup4** pour lire les fichiers html.

### Objet `MinimalCrawler`

Ce crawler correspond au crawler minimal demandé. Il est single-threaded, ce qui signifie que toutes les opérations sont réalisées séquentiellement.

### Constructeur

Cet objet `MinimalCrawler` initialise six attributs lors de son instanciation. Ils sont définis tel que suit :
```python
class MinimalCrawler():

    def __init__(self, start_url, max_urls_crawled=50, max_urls_per_page=5, crawl_delay=5, robot_delay=3, timeout_delay=5):
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

- `__write_visited_urls(self, urls, path, filename)` : écrit une liste d'URLs dans un fichier dans un dossier spécifié.
- `__scan_links_in_page(self, page_url)` : parse l'HTML de la page et extrait des liens vers des pages pouvant elles-mêmes être parsées.
- `__is_crawlable(self, page_url)` : vérifie s'il est possible de parser une page suivant les règles du fichier `robots.txt`.
- `crawl(self, filename, path)` : crawl complet, appelle les autres méthodes et s'arrête quand un certain nombre de liens ont été visités ou lorsque la frontier est vide.

### Objet `Crawler`

### Constructeur

`Crawler` a les mêmes 6 attributs que `MinimalCrawler`. 

### Méthodes

Ce crawler a des méthodes supplémentaires qui permettent la lecture des **sitemaps.xml** des sites web ainsi que la sauvegarde des URLs avec leur âge dans la base de données. Ces méthodes sont les suivantes :

- `__write_visited_urls(self, urls, path, filename)` : écrit une liste d'URLs dans un fichier dans un dossier spécifié.
- `__scan_links_in_page(self, page_url)` : parse l'HTML de la page et extrait des liens vers des pages pouvant elles-mêmes être parsées.
- `__is_crawlable(self, page_url)` : vérifie s'il est possible de parser une page suivant les règles du fichier `robots.txt`.
- `crawl(self, filename, path)` : crawl complet, appelle les autres méthodes et s'arrête quand un certain nombre de liens ont été visités ou lorsque la frontier est vide.

## Utilisation

### `MinimalCrawler`

Le crawler dans la version demandée en base pour le TP peut être utilisé avec le code suivant.

```python
from minimalcrawler import MinimalCrawler

if __name__=="__main__":
    start_url = 'https://ensai.fr/'
    mincrawler = MinimalCrawler(start_url)
    mincrawler.crawl()
```
Il suffit de lui passer en attribut l'URL de départ puis d'appeler la méthode `crawl()` pour lancer le crawler et écrire les URL visitées dans un fichier `crawled_webpages.txt`.

### `Crawler`
