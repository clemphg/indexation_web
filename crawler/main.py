
from minimalcrawler import MinimalCrawler
from crawler import Crawler


def main():
    pass


if __name__=="__main__":

    start_url = 'https://ensai.fr/'
    
    #mincrawler = MinimalCrawler(start_url)
    #mincrawler.crawl(path='crawler', filename='crawled_webpages.txt')

    crawler = Crawler(start_url, 10)
    crawler.crawl(path='crawler', filename='crawled_webpages2.txt')