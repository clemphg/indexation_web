from protego import Protego
from urllib.parse import urlparse, urlunparse
import os
import time

from bs4 import BeautifulSoup

from urllib.request import urlopen

base_url = "https://ensai.fr/portes-ouvertes/"
parsed_url = urlparse(base_url)
home_page_url = parsed_url.scheme+'://'+parsed_url.netloc

print("Home page url:",home_page_url)


with urlopen(base_url) as response:
    html = response.read()
soup = BeautifulSoup(html, 'html.parser')

outgoing_links = [a['href'] for a in soup.find_all('a', href=True) if not a['href'].startswith('#')]



rp = Protego()


with urlopen(os.path.join(home_page_url,"robots.txt")) as response:
    robots_txt_content = response.read().decode("utf-8")

rp.parse(robots_txt_content)

outgoing_links_ok = []

for link in outgoing_links:
    if rp.can_fetch("*", base_url):
        outgoing_links_ok.append(link)
        time.sleep(3)

# remove contents of destination text file
open('protego.txt', "w").close()

        # write urls in filename
with open('protego.txt', 'a') as file:
    for url in outgoing_links_ok:
        file.write(url + '\n')

print(len(outgoing_links_ok))

