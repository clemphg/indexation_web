import urllib.request
from bs4 import BeautifulSoup
import time
from urllib.robotparser import RobotFileParser
import os


def scan_links_in_page(pageurl):

    with urllib.request.urlopen(pageurl) as response:
        html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    links = [a['href'] for a in soup.find_all('a', href=True)]

    # drop duplicates
    links = list(set(links))

    # check rules for each url
    # only keep those that can be accesses
    rp = RobotFileParser(os.path.join(pageurl,"robots.txt"))
    allowed_links = [url for url in links if rp.can_fetch("*", url)]
    print(allowed_links)

    return links

def write_urls(urls, filename="crawled_webpages.txt"):
    with open(filename, 'a') as file:
        for url in urls:
            file.write(url + '\n')

