
from crawler.minimalcrawler import MinimalCrawler



def main():
    pass


if __name__=="__main__":

    start_url = 'https://ensai.fr/'
    crawler = MinimalCrawler(start_url, 20)

    crawler.crawl()

