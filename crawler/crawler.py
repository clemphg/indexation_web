
import os
import time

from bs4 import BeautifulSoup

from urllib.request import urlopen
from urllib.error import URLError
from urllib.robotparser import RobotFileParser

from urllib.parse import urlparse


class Crawler():

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
        rp: RobotFileParser
            Parser for /robots.txt files
        """
        self.seed = start_url

        self.max_urls_crawled = max_urls_crawled
        self.max_urls_per_page = max_urls_per_page

        self.crawl_delay = crawl_delay # seconds
        self.robot_delay = robot_delay # seconds

        self.rp = RobotFileParser(self.seed)
    

    def write_visited_urls(self, urls, filename):

        # remove contents of destination text file
        open(filename, "w").close()

        # write urls in filename
        with open(filename, 'a') as file:
            for url in urls:
                file.write(url + '\n')
    
    def scan_links_in_page(self, page_url):
        """Scans page for outgoing links
        
        Parameter
        ---------
        page_url: str
            Url of the page to crawl
        
        Returns
        -------
        tuple(boolean, list)
            First element is True if no exceptions were raised, and in this case the list contains 
            all outgoing links.
            If first element is False, then the results list is empty
        """
        try:

            with urlopen(page_url) as response:
                html = response.read()
            soup = BeautifulSoup(html, 'html.parser')

            # list all outgoing links from page and remove duplicates
            outgoing_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith('http') and ' ' not in a['href']] # dont consider # (section) and other formats (tel etc)
            outgoing_links = list(set(outgoing_links))

            return True, outgoing_links


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

        self.rp.set_url(os.path.join(home_page_url,"robots.txt"))
        self.rp.read()

        return self.rp.can_fetch("*", page_url)

    def crawl(self, filename='crawled_webpages.txt'):
        """
        Crawls from the given seed (start url)        
        """
        to_crawl = [self.seed]
        crawled = set()

        while to_crawl and len(crawled)<self.max_urls_crawled:

            # we will crawl the first url from the to_crawl list
            current_url = to_crawl.pop(0)

            print(f"[{len(crawled)+1}/{self.max_urls_crawled}] | {current_url}")

            # we do not crawl an already crawled page
            if current_url in crawled:
                print("Page already crawled. Testing another page...")
                continue

            outgoing_links = self.get_links_one_page(current_url)
            if outgoing_links:
                to_crawl.extend(outgoing_links)
                crawled.add(current_url)

            time.sleep(self.crawl_delay)
            
        # write results
        self.write_visited_urls(list(crawled), filename)
    
    def get_sitemaps(self, url):
        """Get sitemaps from a website, returns None if not sitemap is exposed"""

        parsed_url = urlparse(url)
        home_page_url = parsed_url.scheme+'://'+parsed_url.netloc
        self.rp.set_url(os.path.join(home_page_url,"robots.txt"))
        self.rp.read()

        return self.rp.site_maps() # None if no sitemaps

    def scan_sitemap(self, sitemap):
        """Scans a sitemap and returns all pages exposed by the sitemap (if they can be crawled)"""

        with urlopen(sitemap) as response:
            xml_content = response.read()

        soup = BeautifulSoup(xml_content, 'xml')

        urls = [loc.text.strip() for loc in soup.find_all('loc')]

        return urls

    def scan_urls_from_sitemap(self, url):
        """Get urls of pages exposed by sitemaps for the whole website"""

        # get all sitemaps from website
        sitemaps = self.get_sitemaps(url)
        time.sleep(self.robot_delay) # to respect politeness

        if sitemaps:
            result_urls = set()

            for sitemap in sitemaps:
                urls = self.scan_sitemap(sitemap)

                # remove previously scanned sitemaps from urls
                cleaned_urls = [url for url in urls if url not in sitemaps and url.startswith('http') and ' ' not in url]
                
                # add newly found pages to result
                result_urls = result_urls.union(set(cleaned_urls))
            return list(result_urls)
        
        return False, []
    
    def get_links_one_page(self, url):

        sitemap_urls = self.scan_urls_from_sitemap(url)[1]
        page_outgoing_urls = self.scan_links_in_page(url)[1]

        all_urls = list(set(sitemap_urls).union(set(page_outgoing_urls)))

        all_urls = [url for url in all_urls if url.startswith('http') and ' ' not in url]

        if len(all_urls)==0:
            return None

        ok_urls = []
        tested_urls = 0

        # get list of ok urls of max(len) = self.max_urls_per_page 
        while len(ok_urls)<self.max_urls_per_page and tested_urls<len(all_urls):
            print(all_urls[tested_urls])
            if self.is_crawlable(all_urls[tested_urls]):
                ok_urls.append(all_urls[tested_urls])
                time.sleep(self.robot_delay)
            tested_urls+=1

        return ok_urls

