"""
Minimal crawler implementation
"""
import os
import time
import socket

from urllib.request import urlopen
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

from bs4 import BeautifulSoup

# handling errors
from urllib.error import URLError
from http.client import BadStatusLine

class MinimalCrawler():

    def __init__(self, 
                 start_url:str, 
                 max_urls_crawled:int=50, 
                 max_urls_per_page:int=5,
                 crawl_delay:int=5, 
                 robot_delay:int=3,
                 timeout_delay:int=5) -> None:
        """
        Attributes
        ----------
        __seed: url
            Start url for the crawler.
        __max_urls_crawled: int
            Maximum number of distinct urls to crawl, default = 50.
        __max_urls_per_page: int
            Maximum number of urls to crawl from each page, default = 5.
        __crawl_delay: int
            Time in seconds to wait for before crawling another page, default = 5.
        __robot_delay: int
            Time in seconds to wait before interrogating another /robots.txt (politeness), default = 3.
        __timeout_seconds: int
            Time in seconds to try to fetch an url, default = 5.
        """
        self.__seed = start_url

        self.__max_urls_crawled = max_urls_crawled
        self.__max_urls_per_page = max_urls_per_page

        self.__crawl_delay = crawl_delay  # seconds
        self.__robot_delay = robot_delay  # seconds
        self.__timeout_delay = timeout_delay # seconds

    def __write_visited_urls(self, urls:list[str], path:str, filename:str) -> None:
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

    def __scan_links_in_page(self, page_url:str) -> (bool, list[str]):
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
            # parse the page
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
            outgoing_links = [a['href'] for a in soup.find_all('a', href=True) 
                              if a['href'].startswith('http') and ' ' not in a['href']
                              and a['href'].endswith(('.html', '.htm', '/'))]  # dont consider # (section) and other formats (tel etc)
            outgoing_links = list(set(outgoing_links))

            # only select a certain number (or less) of crawlable outgoing links
            links_selection = []
            tested_outgoing_links = 0

            while len(links_selection) < self.__max_urls_per_page and tested_outgoing_links < len(outgoing_links):

                if self.__is_crawlable(outgoing_links[tested_outgoing_links]):
                    links_selection.append(
                        outgoing_links[tested_outgoing_links])
                    
                    # delay to satisfy politeness between robots.txt accesses
                    time.sleep(self.__robot_delay)

                tested_outgoing_links += 1

            return True, links_selection

        except URLError as e:
            print(f"Error opening the URL: {e}")
            return False, []
        except TimeoutError:
            print(f"Timeout occurred. Connection timed out after {self.__timeout_delay} seconds.")
            return False, []

    def __is_crawlable(self, page_url:str) -> bool:
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
        try:
            # parsing the url to retrieve the home page url
            parsed_url = urlparse(page_url)
            home_page_url = parsed_url.scheme+'://'+parsed_url.netloc

            # instanciating the robots.txt file parser
            rp = RobotFileParser()
            rp.set_url(os.path.join(home_page_url, "robots.txt"))

            try: 
                socket.setdefaulttimeout(self.__timeout_delay)
                rp.read()
                # returns True if page is crawlable, False otherwise
                return rp.can_fetch("*", page_url)
            except BadStatusLine as e:
                print(f"BadStatusLine error: {e}")
                return False
            except (URLError, socket.timeout) as e:
                print(f"Error fetching robots.txt: {e}")
                return False
        except URLError as e:
            print(f"URLError: {e}")
            return False

    def crawl(self, filename:str, path:str) -> None:
        """Crawls from the given seed (start url).

        Parameters
        ----------
        filename: str
            Name of file containing the URLs.
        path: str
            Path to folder in which the file will be saved.

        Returns
        -------
        None
        """
        frontier = [self.__seed]
        crawled = set() # parsed URLs

        while frontier and len(crawled) < self.__max_urls_crawled:

            # we will crawl the first url from the frontier
            current_url = frontier.pop(0)

            # some verbose to follow the process
            print(f"[{len(crawled)+1}/{self.__max_urls_crawled}] {current_url}")

            # we do not crawl an already crawled page
            if current_url in crawled:
                print("Page already crawled. Moving on...")
                continue

            # parse page and get up to self.__max_urls_per_page outgoing URLs
            response = self.__scan_links_in_page(current_url)
            # if the page has been scanned and the links retrieved (no exception raised)
            if response[0]:
                outgoing_links = response[1]

                # adding new outgoing links to the frontier
                frontier.extend(outgoing_links)

                # adding the current url to the list of visited URLs
                crawled.add(current_url)

            # waiting some time before parsing another page
            time.sleep(self.__crawl_delay)

        # write results into file
        self.__write_visited_urls(list(crawled), path, filename)
