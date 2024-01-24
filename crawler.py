import os
import time

from bs4 import BeautifulSoup

from urllib.request import urlopen
from urllib.robotparser import RobotFileParser

from urllib.parse import urlparse, urlunparse


class Crawler():

    def __init__(self, start_url):
        self.seed = start_url
        self.to_visit = []
        self.visited = []
        self.max_urls = 5
        self.crawl_delay = 5 # seconds
        self.hascrawled = False
    

    def write_visited_urls(self, filename='crawled_webpages.txt', clear=True):

        # remove contents of destination text file
        open(filename, "w").close()

        # write urls in filename
        with open(filename, 'a') as file:
            for url in self.visited:
                file.write(url + '\n')
    
    def scan_links_in_page(self, page_url):

        # initalise robot file parser (to only keep allowed urls)
        rp = RobotFileParser(os.path.join(page_url,"robots.txt"))
        rp.read()

        with urlopen(page_url) as response:
            html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        allowed_links = [a['href'] for a in soup.find_all('a', href=True) if rp.can_fetch("*", a['href'])]

        # drop duplicates
        allowed_links = list(set(allowed_links))

        return allowed_links
    
    def is_crawlable(self, url):
        """True if page is crawlable, False otherwise"""
        parsed_url = urlparse(url)
        home_page_url = urlunparse((parsed_url.scheme, parsed_url.netloc, '', '', '', ''))
        rp = RobotFileParser(os.path.join(home_page_url,"robots.txt"))
        rp.read()
        return rp.can_fetch("*", url)

    def crawl(self):
        if not self.hascrawled:
            to_crawl = [self.seed]
            crawled = set()

            while to_crawl and len(crawled)<self.max_urls:

                current_url = to_crawl.pop(0)

                print("Current url:", current_url)

                if current_url in crawled:
                    continue

                outgoing_links = self.scan_links_in_page(current_url)

                links_to_add = []
                tested_outgoing_links = 0

                # add five f=links which can be visited
                while len(links_to_add)<5 and tested_outgoing_links<len(outgoing_links):
                    if self.is_crawlable(outgoing_links[tested_outgoing_links]):
                        links_to_add.append(outgoing_links[tested_outgoing_links])
                        time.sleep(3)
                    tested_outgoing_links+=1

                print(links_to_add)
                to_crawl.extend(links_to_add)

                crawled.add(current_url)
                print(crawled)
                time.sleep(5)
            
            # write results
            self.visited = list(crawled)
            self.write_visited_urls()

        else:
            print("This crawler has already been crawling")