
from crawler import Crawler

def main():
    pass

if __name__=="__main__":

    start_url = 'https://ensai.fr/'

    crawler = Crawler(start_url)

    urls = crawler.scan_links_in_page(start_url)

    print(len(urls))
    # 220 with robots.txt

    crawler.write_visited_urls("test.txt")

