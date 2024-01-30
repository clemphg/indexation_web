
import argparse
import time

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

    crawler = Crawler(args.seed, int(args.max_urls_to_crawl), 15)

    start_time = time.time()
    crawler.crawl(path='crawler', filename='crawled_webpages3.txt')

    print(f"\n{time.time()-start_time}s")

if __name__=="__main__":
    main()

