from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse, urlunparse
import os

base_url = "https://www.instagram.com/ensai_rennes/"
parsed_url = urlparse(base_url)
home_page_url = urlunparse((parsed_url.scheme, parsed_url.netloc, '', '', '', ''))

print(home_page_url)

rp = RobotFileParser()
rp.set_url(os.path.join(home_page_url,"robots.txt"))
rp.read()
print(rp.can_fetch("*", base_url))
