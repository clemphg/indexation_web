from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse, urlunparse
import os

from bs4 import BeautifulSoup

from urllib.request import urlopen

base_url = "https://www.facebook.com/Ensai35/"
parsed_url = urlparse(base_url)
home_page_url = parsed_url.scheme+'://'+parsed_url.netloc

print(home_page_url)

rp = RobotFileParser()
rp.set_url(os.path.join(home_page_url,"robots.txt"))
rp.read()
print(rp.can_fetch("*", base_url))


#with urlopen(base_url) as response:
#    html = response.read()
#soup = BeautifulSoup(html, 'html.parser')

#outgoing_links = [a['href'] for a in soup.find_all('a', href=True) if not a['href'].startswith('#')]


#print(outgoing_links)