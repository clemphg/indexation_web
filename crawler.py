import os
import time

from bs4 import BeautifulSoup

from urllib.request import urlopen
from urllib.robotparser import RobotFileParser

class Crawler():

    def __init__(self, start_url):
        self.start_url = start_url
        self.to_visit = []
        self.visited = []
        self.max_urls = 50
        self.crawl_delay = 5 # seconds
    

    def write_visited_urls(self, filename='crawled_webpages.txt', clear=True):

        # remove contents of destination text file
        open(filename, "w").close()

        # write urls in filename
        with open(filename, 'a') as file:
            for url in self.visited:
                file.write(url + '\n')
    
    def scan_links_in_page(self, pageurl):

        # initalise robot file parser (to only keep allowed urls)
        rp = RobotFileParser(os.path.join(pageurl,"robots.txt"))

        with urlopen(pageurl) as response:
            html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        links = [a['href'] for a in soup.find_all('a', href=True)]

        #links = [a['href'] for a in soup.find_all('a', href=True) if rp.can_fetch("*", a['href'])]

        # drop duplicates
        links = list(set(links))

        # check rules for each url, only keep those that can be accesses
        allowed_links = [url for url in links if rp.can_fetch("*", url)]

        return allowed_links

    def crawl(self):
        pass