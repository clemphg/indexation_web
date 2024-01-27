"""
Testing both robots
"""

import os
import time

from urllib.parse import urlparse
from urllib.request import urlopen
from urllib.robotparser import RobotFileParser

from protego import Protego

def test_robotfileparser(url):
    time.sleep(3)

    parsed_url = urlparse(url)
    home_page_url = parsed_url.scheme+'://'+parsed_url.netloc+'/'
    print("Home page url:", home_page_url)

    rp = RobotFileParser()
    rp.set_url(os.path.join(home_page_url, "robots.txt"))
    rp.read()

    return rp.can_fetch("*", url)

def test_protego(url):
    time.sleep(3)

    parsed_url = urlparse(url)
    home_page_url = parsed_url.scheme+'://'+parsed_url.netloc
    print("Home page url:", home_page_url)

    rp = Protego()
    with urlopen(os.path.join(home_page_url, "robots.txt")) as response:
        robots_txt_content = response.read().decode("utf-8")

    rp.parse(robots_txt_content)

    return rp.can_fetch(url, "*")


li = [
    "https://www.linkedin.com/school/ecole-nationale-de-la-statistique-et-de-l'analyse-de-l'information/",
    "https://ensai.fr/"
]

for url in li:
    print(test_robotfileparser(url))



#print(test_robotfileparser("https://www.instagram.com/ensai_rennes/", rp1))

#print(test_protego("https://twitter.com/", rp2))
#print(test_protego("https://www.instagram.com/", rp2))


robotstxt = """
User-agent: *
Disallow: /
Allow: /about
Allow: /account
Disallow: /account/contact$
Disallow: /account/*/profile
Crawl-delay: 4
Request-rate: 10/1m                 # 10 requests every 1 minute

Sitemap: http://example.com/sitemap-index.xml
Host: http://example.co.in
"""

#rp = Protego.parse(robotstxt)
#print(rp.can_fetch("http://example.com/", "*"))