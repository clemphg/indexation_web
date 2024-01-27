"""
Minimal crawler implementation
"""
import os
import time

from urllib.request import urlopen
from urllib.error import URLError
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse

from bs4 import BeautifulSoup
import http.client


class MinimalCrawler():

    def __init__(self, start_url, max_urls_crawled=50, max_urls_per_page=5, crawl_delay=5, robot_delay=3):
        """
        Attributes
        ----------
        seed: url
            Start url for the crawler
        max_urls_crawled: int
            Maximum number of distinct urls to crawl
        max_urls_per_page: int
            Maximum number of urls to crawl from each page
        crawl_delay: int
            Time in seconds to wait for before crawling another page
        robot_delay: int
            Time in seconds to wait before interrogating another /robots.txt (politeness)
        """
        self.seed = start_url

        self.max_urls_crawled = max_urls_crawled
        self.max_urls_per_page = max_urls_per_page

        self.crawl_delay = crawl_delay  # seconds
        self.robot_delay = robot_delay  # seconds

    def write_visited_urls(self, urls, filename='crawler/crawled_webpages.txt'):

        # remove contents of destination text file
        open(filename, "w", encoding='utf-8').close()

        # write urls in filename
        with open(filename, 'a') as file:
            for url in urls:
                file.write(url + '\n')

    def scan_links_in_page(self, page_url):
        """Scans page for outgoing links
        Returns self.max_urls_per_page links of less which can be crawled.

        Parameter
        ---------
        page_url: str
            Url of the page to crawl

        Returns
        -------
        tuple(boolean, list)
            First element is True if no exceptions were raised, and in this case 
            the list contains at most self.max_urls_per_page urls.
            If first element is False, then the results list is empty
        """
        try:

            with urlopen(page_url) as response:
                html = response.read()
            soup = BeautifulSoup(html, 'html.parser')

            # list all outgoing links from page and remove duplicates
            outgoing_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith(
                'http') and ' ' not in a['href']]  # dont consider # (section) and other formats (tel etc)
            outgoing_links = list(set(outgoing_links))

            # only select a certain number (or less) crawlable outgoing links
            links_selection = []
            tested_outgoing_links = 0

            while len(links_selection) < self.max_urls_per_page and tested_outgoing_links < len(outgoing_links):

                if self.is_crawlable(outgoing_links[tested_outgoing_links]):
                    links_selection.append(
                        outgoing_links[tested_outgoing_links])
                    # delay to satisfy politeness between robots.txt accesses
                    time.sleep(self.robot_delay)

                tested_outgoing_links += 1

            return True, links_selection

        except URLError as e:
            print(f"Error opening the URL: {e}")
            return False, []

    def is_crawlable(self, page_url):
        """Checks if a page can be crawled by interrogating the /robots.txt file of the website.

        Parameter
        ---------
        page_url: str
            Url of the page to check

        Returns
        -------
        boolean
            True if page is crawlable, False otherwise
        """
        parsed_url = urlparse(page_url)
        home_page_url = parsed_url.scheme+'://'+parsed_url.netloc

        rp = RobotFileParser()
        rp.set_url(os.path.join(home_page_url, "robots.txt"))

        try: 
            rp.read()
            return rp.can_fetch("*", page_url)
        except http.client.BadStatusLine as e:
            print(f"BadStatusLine error: {e}")
            return False

    def crawl(self):
        """
        Crawls from the given seed (start url)        
        """
        to_crawl = [self.seed]
        crawled = set()

        while to_crawl and len(crawled) < self.max_urls_crawled:

            # we will crawl the first url from the to_crawl list
            current_url = to_crawl.pop(0)

            print(f"[{len(crawled)+1}/{self.max_urls_crawled}] | {current_url}")

            # we do not crawl an already crawled page
            if current_url in crawled:
                print("Page already crawled. Testing another page...")
                continue

            response = self.scan_links_in_page(current_url)
            # if the page has been scanned and the links retrieved (no exception raised)
            if response[0]:
                outgoing_links = response[1]
                to_crawl.extend(outgoing_links)

                crawled.add(current_url)

            time.sleep(self.crawl_delay)

        # write results
        self.write_visited_urls(list(crawled))
