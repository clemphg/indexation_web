
from crawler import Crawler

def main():
    pass

if __name__=="__main__":

    start_url = 'https://ensai.fr/'

    crawler = Crawler(start_url)

    crawler.crawl()

