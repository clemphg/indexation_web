from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
import os
import time

from bs4 import BeautifulSoup

from urllib.request import urlopen

base_url = "https://ensai.fr"
parsed_url = urlparse(base_url)
home_page_url = parsed_url.scheme+'://'+parsed_url.netloc

with urlopen(base_url) as response:
    html = response.read()
soup = BeautifulSoup(html, 'html.parser')

outgoing_links = list(set([a['href'] for a in soup.find_all('a', href=True) if not a['href'].startswith('#')]))
print(len(outgoing_links))

states = []


for link in outgoing_links:
    parsed_url = urlparse(link)
    home_page_url = parsed_url.scheme+'://'+parsed_url.netloc

    rp = RobotFileParser()
    rp.set_url(os.path.join(home_page_url, "robots.txt"))
    rp.read()
    time.sleep(3)

    state = rp.can_fetch("*", link)
    states.append(state)

    print(link)
    print("->",state)

    if len(states) == 20:
        break


# remove contents of destination text file
open('robotfileparser2.txt', "w").close()

# write urls in filename
with open('robotfileparser2.txt', 'a') as file:
    for url, state in zip(outgoing_links, states):
        file.write(url + ',' + str(state) + '\n')

print(len(outgoing_links))
