
from minimalcrawler import MinimalCrawler
from crawler import Crawler


def main():
    pass


if __name__=="__main__":

    start_url = 'https://ensai.fr/'
    mincrawler = MinimalCrawler(start_url, 50)

    mincrawler.crawl(path='/crawler')

    #crawler = Crawler(start_url, 10)
    #crawler.crawl('test.txt')
