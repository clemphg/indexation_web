
import argparse

from minimalcrawler import MinimalCrawler
from crawler import Crawler


def main():

    # parsing arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("seed", default='https://ensai.fr/')
    parser.add_argument("max_urls_to_crawl", default=50)
    args = parser.parse_args()

    start_url = 'https://ensai.fr/'
    
    #mincrawler = MinimalCrawler(start_url)
    #mincrawler.crawl(path='crawler', filename='crawled_webpages.txt')

    crawler = Crawler(args.seed, int(args.max_urls_to_crawl))
    crawler.crawl(path='crawler', filename='crawled_webpages3.txt')


if __name__=="__main__":
    main()

