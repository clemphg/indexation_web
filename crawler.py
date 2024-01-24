import os
import time

from bs4 import BeautifulSoup

import ssl
from urllib.request import urlopen
from urllib.error import URLError
from urllib.robotparser import RobotFileParser

from urllib.parse import urlparse, urlunparse


class Crawler():

    def __init__(self, start_url, max_urls_crawled=50, max_urls_per_page=5, crawl_delay=5, robot_delay=3):
        self.seed = start_url

        self.max_urls_crawled = max_urls_crawled
        self.max_urls_per_page = max_urls_per_page

        self.crawl_delay = crawl_delay # seconds
        self.robot_delay = robot_delay # seconds

        self.rp = RobotFileParser(self.seed)
    

    def write_visited_urls(self, urls, filename='crawled_webpages.txt'):

        # remove contents of destination text file
        open(filename, "w").close()

        # write urls in filename
        with open(filename, 'a') as file:
            for url in urls:
                file.write(url + '\n')
    
    def scan_links_in_page(self, page_url):
        """Scans page for outgoing links
        Returns self.max_urls_per_page links of less which can be crawled."""
        try:
            # Create an SSL context with custom settings
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            with urlopen(page_url, context=ssl_context) as response:
                html = response.read()
            soup = BeautifulSoup(html, 'html.parser')

            # list all outgoing links from page and remove duplicates
            outgoing_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith('http') and ' ' not in a['href']] # dont consider # (section) and other formats (tel etc)
            outgoing_links = list(set(outgoing_links))

            # only select a certain number (or less) crawlable outgoing links
            links_selection = []
            tested_outgoing_links = 0

            while len(links_selection)<self.max_urls_per_page and tested_outgoing_links<len(outgoing_links):

                if self.is_crawlable(outgoing_links[tested_outgoing_links]):
                    links_selection.append(outgoing_links[tested_outgoing_links])
                    time.sleep(self.robot_delay) # delay to satisfy politeness between robots.txt accesses

                tested_outgoing_links+=1

            return links_selection


        except URLError as e:
            print(f"Error opening the URL: {e}")
            return []


    
    def is_crawlable(self, page_url):
        """True if url page is crawlable, False otherwise"""
        parsed_url = urlparse(page_url)
        home_page_url = parsed_url.scheme+'://'+parsed_url.netloc

        self.rp.set_url(os.path.join(home_page_url,"robots.txt"))
        self.rp.read()

        return self.rp.can_fetch("*", page_url)

    def crawl(self):
        to_crawl = [self.seed]
        crawled = set()

        while to_crawl and len(crawled)<self.max_urls_crawled:

            # we will crawl the first url from the to_crawl list
            current_url = to_crawl.pop(0)

            print("Current url:", current_url)

            # to crawl or not to crawl
            if current_url in crawled:
                continue

            outgoing_links = self.scan_links_in_page(current_url)
            to_crawl.extend(outgoing_links)

            crawled.add(current_url)

            if len(crawled)%1==0:
                print(f"{len(crawled)} crawled")

            time.sleep(self.crawl_delay)
            
        # write results
        self.write_visited_urls(list(crawled))