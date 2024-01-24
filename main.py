
from functions import scan_links_in_page, write_urls

def main():
    pass

if __name__=="__main__":

    start_url = 'https://ensai.fr/'
    urls = scan_links_in_page(start_url)

    print(len(urls))
    # 220 with robots.txt

    write_urls(urls, "test.txt")


