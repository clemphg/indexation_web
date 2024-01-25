
import os
import time

import urllib.request
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

from bs4 import BeautifulSoup


def get_sitemaps(url):
    parsed_url = urlparse(url)
    home_page_url = parsed_url.scheme+'://'+parsed_url.netloc

    rp = RobotFileParser()
    rp.set_url(os.path.join(home_page_url,"robots.txt"))
    rp.read()

    return rp.site_maps() # None if no sitemaps


def scan_sitemap(sitemap):

    with urllib.request.urlopen(sitemap) as response:
        xml_content = response.read()

    soup = BeautifulSoup(xml_content, 'xml')

    urls = [loc.text.strip() for loc in soup.find_all('loc')]

    return urls

def scan_urls_from_sitemap(url):

    # get all sitemaps from website
    sitemaps = get_sitemaps(url)
    time.sleep(3) # to respect politeness

    if sitemaps:
        result_urls = set()

        for sitemap in sitemaps:
            urls = scan_sitemap(sitemap)

            # remove previously scanned sitemaps from urls
            cleaned_urls = [url for url in urls if url not in sitemaps]
            
            # add newly found pages to result
            result_urls = result_urls.union(set(cleaned_urls))
        return list(result_urls)
    
    return None


pageurl = 'https://ensai.fr/category-sitemap.xml'

urls = scan_urls_from_sitemap(pageurl)

for url in urls:
    print(url)

