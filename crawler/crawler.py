"""
Crawler with MinimalCrawler components + bonuses
"""
import os
import time
import socket
import sqlite3

from urllib.request import urlopen
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

from bs4 import BeautifulSoup

# handling errors
from urllib.error import URLError
from http.client import BadStatusLine, IncompleteRead

class Crawler():

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
        __seed: str
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
        # parsing the url to retrieve the home page url
        try:
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
    
    def __get_sitemaps(self, url:str) -> (list[str]|None):
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

    def __scan_sitemap(self, sitemap:str) -> list[str]:
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

    def __scan_urls_from_sitemap(self, url:str) -> (bool, list[str]):
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
            sitemaps = self.__get_sitemaps(url)
            time.sleep(self.__robot_delay) 


            parsed_url = urlparse(url)
            home_page_url = parsed_url.scheme+'://'+parsed_url.netloc

            # instanciating the robots.txt file parser
            rp = RobotFileParser()
            rp.set_url(os.path.join(home_page_url, "robots.txt"))

            if sitemaps:
                result_urls = set()

                for sitemap in [st for st in sitemaps if st.startswith('http')]:
                    urls = self.__scan_sitemap(sitemap)

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
    
    def __get_links_one_page(self, url:str) -> (list[str]|None):
        """Get list of URL to add to the frontier from the url given.

        Adds up to self.__max_urls_per_page

        Parameters
        ----------
        url: str
            URL of page to crawl
        
        Returns
        -------
        list[str]
            List of URLs to add to the frontier, None if no links.
        """
        sitemap_urls = self.__scan_urls_from_sitemap(url)[1] # can all be crawled
        page_outgoing_urls = self.__scan_links_in_page(url)[1] 

        all_urls = list(set(sitemap_urls).union(set(page_outgoing_urls)))

        all_urls = [url for url in all_urls if url.startswith('http') and ' ' not in url]

        if len(all_urls)==0:
            return None

        ok_urls = []
        tested_urls = 0

        # get list of ok urls of max(len) = self.max_urls_per_page 
        while len(ok_urls)<self.__max_urls_per_page and tested_urls<len(all_urls):
            if all_urls[tested_urls] in sitemap_urls: # already checked that those are crawlable
                ok_urls.append(all_urls[tested_urls])
            elif self.__is_crawlable(all_urls[tested_urls]):
                ok_urls.append(all_urls[tested_urls])
                time.sleep(self.__robot_delay)
            tested_urls+=1

        return ok_urls

    def __db_create_table(self, tablename:str, dbname:str, path:str) -> str:
        """Create table in database
        
        Parameters
        ----------
        tablename: str
            Name of the table to create to store the urls and their age.
        dbname: str
            Name of the database.
        path: str
            Path of the folder containing the database
        """
        # connecting to the db
        con = sqlite3.connect(os.path.join(path,dbname))
        cur = con.cursor()

        # get list of tables in the database
        res = cur.execute("SELECT name FROM sqlite_master")
        tablenames = [name[0] for name in res.fetchall()]

        # useful if table does not already exists
        new_tablename = tablename

        # if table already exists
        if tablename in tablenames:
            ind = 1
            new_tablename = tablename + '_' + str(ind)

            # increase until no table matches the name
            while new_tablename in tablenames:
                ind += 1
                new_tablename = tablename + '_' + str(ind)
            
            print(f"Table {tablename} already exists in {os.path.join(path,dbname)}. Writing into {new_tablename} instead...\n")

        # creating the table
        cur.execute(f"CREATE TABLE {new_tablename}(url TEXT PRIMARY KEY, age INTEGER)")  # Specify column names and types
        con.commit()

        cur.close()
        con.close()

        return new_tablename # in case the tablename changed, to insert the urls later on


    def __db_add_url(self, url:str, tablename:str, dbname:str, path:str) -> None:
        """Add url to the database and increases the age of URLs already in the databse.

        Parameters
        ----------
        url: str
            URL to add to the database.
        tablename: str
            Name of the table to create to store the urls and their age.
        dbname: str
            Name of the database.
        path: str
            Path of the folder containing the database
        """
        # connecting to the db
        con = sqlite3.connect(os.path.join(path, dbname))
        cur = con.cursor()

        try:
            # update ages of urls already in table
            cur.execute(f"UPDATE {tablename} SET age = age + 1;")
            con.commit()

            # check if url is already in table
            query = f"SELECT COUNT(*) FROM {tablename} WHERE url = ?;"
            cur.execute(query, (url,))
            already_in = cur.fetchone()[0]>0

            if not already_in:
                # insert url into table
                query = f"INSERT INTO {tablename} (url, age) VALUES (?, ?);"
                con.execute(query, (url, 0))
                con.commit()
            else:
                # set age to 0 if url was already in table
                query = f"UPDATE {tablename} SET age = 0 WHERE url = ?;"
                con.execute(query, (url,))
                con.commit()
        
        except Exception as e:
            print(f"Error: {e}")
        finally:
            cur.close()
            con.close()

    def crawl(self, filename:str, dbname:str, tablename:str, path:str) -> None:
        """Crawls from the given seed (start url).

        Parameters
        ----------
        filename: str
            Name of file containing the URLs.
        dbname: str
            Name of the database in which to store the ages.
        tablename: str
            Name of the table in the datatabase to store the ages.
        path: str
            Path to folder in which the file will be saved.

        Returns
        -------
        None
        """
        # initalise db / ages table
        tablename = self.__db_create_table(tablename, dbname, path)

        frontier = [self.__seed]
        crawled = set() # parsed URLs

        while frontier and len(crawled)<self.__max_urls_crawled:

            # we will crawl the first url from the frontier
            current_url = frontier.pop(0) 

            # some verbose to follow the process
            print(f"[{len(crawled)+1}/{self.__max_urls_crawled}] {current_url}")

            # we do not crawl an already crawled page (could be changed later)
            if current_url in crawled:
                print("Page already crawled. Moving on...")
                continue

            # get list of links from page as well as sitemap
            # this list contains at most self.__max_urls_per_page elements
            outgoing_links = self.__get_links_one_page(current_url)

            if outgoing_links:
                frontier.extend(outgoing_links)
                crawled.add(current_url)

                # add crawled url to the database + increment other url's age by 1
                self.__db_add_url(current_url, tablename, dbname, path)

            time.sleep(self.__crawl_delay)
        
        if len(frontier)==0:
            print("No more links to explore.")

        # write results
        self.__write_visited_urls(list(crawled), path, filename)