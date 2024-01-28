"""
Crawler with MinimalCrawler components + bonuses
"""
import os
import time

from urllib.request import urlopen
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

from bs4 import BeautifulSoup

from urllib.error import URLError
from http.client import BadStatusLine, IncompleteRead

class Crawler():

    def __init__(self, 
                 start_url, 
                 max_urls_crawled=50, 
                 max_urls_per_page=5, 
                 crawl_delay=5, 
                 robot_delay=3, 
                 timeout_delay=5):
        """
        Attributes
        ----------
        __seed: url
            Start url for the crawler
        __max_urls_crawled: int
            Maximum number of distinct urls to crawl
        __max_urls_per_page: int
            Maximum number of urls to crawl from each page
        __crawl_delay: int
            Time in seconds to wait for before crawling another page
        __robot_delay: int
            Time in seconds to wait before interrogating another /robots.txt (politeness)
        __timeout_seconds: int
            Time in seconds to try to fetch an url, default = 5.
        """
        self.__seed = start_url

        self.__max_urls_crawled = max_urls_crawled
        self.__max_urls_per_page = max_urls_per_page

        self.__crawl_delay = crawl_delay # seconds
        self.__robot_delay = robot_delay # seconds
        self.__timeout_delay = timeout_delay # seconds
    

    def write_visited_urls(self, urls, path, filename):
        """Writes list of urls into a file

        Parameters
        ----------
        urls: list[str]
            List of URLs.
        path: str
            Path to folder in which the file will be saved.
        filename: str
            Name of file containing the URLs.
        
        Returns
        -------
        None
        """
        if filename in os.listdir(path):
            # remove content of destination text file
            open(os.path.join(path,filename), "w", encoding='utf-8').close()
        else:
            with open(os.path.join(path,filename), "w", encoding='utf-8') as file:
                pass
        # write urls in file
        with open(os.path.join(path,filename), 'a') as file:
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
            with urlopen(page_url, timeout=self.__timeout_delay) as response:
                content = b''
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    content += chunk

                html = content
            soup = BeautifulSoup(html, 'html.parser')

            # list all outgoing links from page and remove duplicates
            # dont consider '#' (section) and other formats (tel etc)
            outgoing_links = [a['href'] for a in soup.find_all('a', href=True) 
                              if a['href'].startswith('http') and ' ' not in a['href']]
            outgoing_links = list(set(outgoing_links))

            return True, outgoing_links

        except URLError as e:
            print(f"Error opening the URL: {e}")
            return False, []
        except TimeoutError:
            print(f"Timeout occurred. Connection timed out after {self.__timeout_delay} seconds.")
            return False, []
        except IncompleteRead as e:
            print(f"IncompleteRead error: {e}")
            # Handle the error by retrying the request or any other appropriate action
            return False, []

    
    def is_crawlable(self, page_url):
        """Checks if a page can be crawled by interrogating the /robots.txt file of the website.

        Parameter
        ---------
        page_url: str
            URL of the page to check.

        Returns
        -------
        boolean
            True if page is crawlable, False otherwise1;
        """
        # parsing the url to retrieve the home page url
        try:
            parsed_url = urlparse(page_url)
            home_page_url = parsed_url.scheme+'://'+parsed_url.netloc

            # instanciating the robots.txt file parser
            rp = RobotFileParser()
            rp.set_url(os.path.join(home_page_url, "robots.txt"))

            try: 
                rp.read()
                # returns True if page is crawlable, False otherwise
                return rp.can_fetch("*", page_url)
            except BadStatusLine as e:
                print(f"BadStatusLine error: {e}")
                return False
        except URLError as e:
            print(f"URLError: {e}")
            return False

    def crawl(self,  path='', filename='crawled_webpages.txt'):
        """Crawls from the given seed (start url).

        Parameters
        ----------
        path: str
            Path to folder in which the file will be saved, default = '/'.
        filename: str
            Name of file containing the URLs, default = 'crawled_webpages.txt'.

        Returns
        -------
        None
        """
        to_crawl = [self.__seed] # frontier
        crawled = set() # parsed URLs

        while to_crawl and len(crawled)<self.__max_urls_crawled:

            # we will crawl the first url from the to_crawl list (frontier)
            current_url = to_crawl.pop(0) 

            print(f"[{len(crawled)+1}/{self.__max_urls_crawled}] {current_url}")

            # we do not crawl an already crawled page
            if current_url in crawled:
                print("Page already crawled. Moving on...")
                continue

            # get all 
            outgoing_links = self.get_links_one_page(current_url)
            if outgoing_links:
                to_crawl.extend(outgoing_links)
                crawled.add(current_url)

            time.sleep(self.__crawl_delay)
        
        if len(to_crawl)==0:
            print("No more links to explore")
        # write results
        self.write_visited_urls(list(crawled), path, filename)
    
    def get_sitemaps(self, url):
        """Get sitemaps from a website, returns None if not sitemap is exposed

        Parameters
        ----------
        url: str
            Website URL.
        
        Returns
        -------
        list[str]
            List of sitemaps of the website, None if there are no sitemaps.
        """

        parsed_url = urlparse(url)
        home_page_url = parsed_url.scheme+'://'+parsed_url.netloc
        rp = RobotFileParser()
        rp.set_url(os.path.join(home_page_url,"robots.txt"))
        rp.read()

        return rp.site_maps() # None if no sitemaps

    def scan_sitemap(self, sitemap):
        """Scans a sitemap and returns all pages exposed by the sitemap (if they can be crawled)

        Parameters
        ----------
        sitemap: str
            URL of a sitemap
        
        Returns
        -------
        list[str]
            List of URLs of html pages exposed in the sitemap, empty list if error raised.
        """
        try:
            with urlopen(sitemap) as response:
                xml_content = response.read()

            soup = BeautifulSoup(xml_content, 'xml')

            urls = [loc.text.strip() for loc in soup.find_all('loc') if loc.text.endswith(('.html', '.htm', '/'))]            
            return urls
        
        except URLError as e:
            print(f"Error fetching sitemap: {e}")
            return []

    def scan_urls_from_sitemap(self, url):
        """Get urls of pages exposed by sitemaps for the whole website

        Parameters
        ----------
        urls: list[str]
            Url of website.
        
        Returns
        -------
        list[str]
            List of all exposed URLs in the website.
        """
        try:
            # get all sitemaps from website
            sitemaps = self.get_sitemaps(url)
            time.sleep(self.__robot_delay) 


            parsed_url = urlparse(url)
            home_page_url = parsed_url.scheme+'://'+parsed_url.netloc

            # instanciating the robots.txt file parser
            rp = RobotFileParser()
            rp.set_url(os.path.join(home_page_url, "robots.txt"))

            if sitemaps:
                result_urls = set()

                for sitemap in sitemaps:
                    urls = self.scan_sitemap(sitemap)

                    # remove previously scanned sitemaps from urls
                    cleaned_urls = [url for url in urls if url not in sitemaps and url.startswith('http') and ' ' not in url]

                    # only keep urls which can be crawled
                    cleaned_urls_ok = [url for url in cleaned_urls if rp.can_fetch('*', url)]
                    
                    # add newly found pages to result
                    result_urls = result_urls.union(set(cleaned_urls_ok))

                return True, list(result_urls)
            return False, []
            
        except URLError as e:
            print(f"URLError: {e}")
            return False, []
    
    def get_links_one_page(self, url):
        """Get list of URL to add to the frontier from the url given.

        Adds up to self.__max_urls_per_page

        Parameters
        ----------
        url: str
            URL of page to crawl
        
        Returns
        -------
        list[str]
            List of URLs to add to the frontier
        """

        sitemap_urls = self.scan_urls_from_sitemap(url)[1] # can all be crawled
        page_outgoing_urls = self.scan_links_in_page(url)[1] 

        all_urls = list(set(sitemap_urls).union(set(page_outgoing_urls)))

        all_urls = [url for url in all_urls if url.startswith('http') and ' ' not in url]

        if len(all_urls)==0:
            return None

        ok_urls = []
        tested_urls = 0

        # get list of ok urls of max(len) = self.max_urls_per_page 
        while len(ok_urls)<self.__max_urls_per_page and tested_urls<len(all_urls):
            print(all_urls[tested_urls])
            if all_urls[tested_urls] in sitemap_urls: # already checked that those are crawlable
                ok_urls.append(all_urls[tested_urls])
            elif self.is_crawlable(all_urls[tested_urls]):
                ok_urls.append(all_urls[tested_urls])
                time.sleep(self.__robot_delay)
            tested_urls+=1

        return ok_urls

