from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
import os
import time

from bs4 import BeautifulSoup

from urllib.request import urlopen

base_url = "https://ensai.fr/portes-ouvertes/"
parsed_url = urlparse(base_url)
home_page_url = parsed_url.scheme+'://'+parsed_url.netloc

print("Home page url:", home_page_url)


with urlopen(base_url) as response:
    html = response.read()
soup = BeautifulSoup(html, 'html.parser')

outgoing_links = [a['href'] for a in soup.find_all(
    'a', href=True) if not a['href'].startswith('#')]


rp = RobotFileParser()
rp.set_url(os.path.join(home_page_url, "robots.txt"))
rp.read()

outgoing_links_ok = []

for link in outgoing_links:
    if rp.can_fetch("*", base_url):
        outgoing_links_ok.append(link)
        time.sleep(3)

# remove contents of destination text file
open('robotfileparser.txt', "w").close()

# write urls in filename
with open('robotfileparser.txt', 'a') as file:
    for url in outgoing_links_ok:
        file.write(url + '\n')

print(len(outgoing_links_ok))
