"""Main to run crawlers"""

import time
import argparse

from minimalcrawler import MinimalCrawler
from crawler.crawler import Crawler


def main():

    # parsing arguments
    parser = argparse.ArgumentParser()

    # to initialize crawler
    parser.add_argument("-s", "--seed", 
                        default='https://ensai.fr/', 
                        help="Start URL for crawler, default 'https://ensai.fr'.",
                        type=str)
    parser.add_argument("-mc", "--max_urls_to_crawl", 
                        default=50, 
                        help="Maximum number of webpages to crawl, default 50.",
                        type=int)
    parser.add_argument("-mp", "--max_urls_per_page", 
                        default=5,
                        help="Maximum number of links to keep for each crawled webpage, default 5.",
                        type=int)
    parser.add_argument("-cd", "--crawl_delay",
                         default=5, 
                         help="Delay between each page crawl, in seconds, default 5.",
                         type=int)
    parser.add_argument("-rd", "--robot_delay",
                         default=3, 
                         help="Politeness for robots.txt file access, in seconds, default 3.",
                         type=int)
    parser.add_argument("-td", "--timeout_delay", 
                        default=5,
                        help="Timeout for urllib.requests.urlopen, in seconds, default 5.",
                        type=int)
    
    # to pass to Crawler.crawl()
    parser.add_argument("-p", "--path", 
                        default='.',
                        help="Path to save results to, default '.'",
                        type=str)
    parser.add_argument("-f", "--filename", 
                        default='crawled_webpages.txt',
                        help="Filename to save crawled webpages URLs, default 'crawled_webpages.txt'.",
                        type=str)
    parser.add_argument("-db", "--dbname", 
                        default='crawled_webpages.db',
                        help="Database name in which crawled webpages URLs and their age are saved, default 'crawled_webpages.db'.",
                        type=str)
    parser.add_argument("-t", "--tablename", 
                        default='webpages_age',
                        help="Name of table in which crawled webpages URLs and their age are saved, default 'webpages_age'.",
                        type=str)
    parser.add_argument("-c", "--crawler", 
                        default='normal',
                        help="Crawler to use, default 'normal'.",
                        type=str,
                        choices=['minimal', 'normal'])

    args = parser.parse_args()

    # initalize crawler
    if args.crawler == 'minimal':
        crawler = MinimalCrawler(args.seed, 
                                 args.max_urls_to_crawl,
                                 args.max_urls_per_page,
                                 args.crawl_delay,
                                 args.robot_delay,
                                 args.timeout_delay)
    else:
        crawler = Crawler(args.seed, 
                          args.max_urls_to_crawl,
                          args.max_urls_per_page,
                          args.crawl_delay,
                          args.robot_delay,
                          args.timeout_delay)
        
    print("---------- Crawler initialized ----------\n")

    start_time = time.time()

    # crawl (db is intialized before crawling by default)
    print("Starting to crawl...\n")

    if args.crawler == 'minimal':
        crawler.crawl(args.filename,
                      args.path)
    else:
        crawler.crawl(args.filename,
                      args.dbname,
                      args.tablename,
                      args.path)

    print(f"\n...crawling took {round(time.time()-start_time,2)}s")

if __name__=="__main__":

    import os
    print(os.listdir())
    main()


