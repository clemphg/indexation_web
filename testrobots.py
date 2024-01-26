"""
Testing both robots
"""

import os
import time

from urllib.parse import urlparse
from urllib.request import urlopen
from urllib.robotparser import RobotFileParser

from protego import Protego

BASE_URL = "https://www.google.com"
parsed_url = urlparse(BASE_URL)
home_page_url = parsed_url.scheme+'://'+parsed_url.netloc

print("Home page url:", home_page_url)


rp = Protego()

# with urlopen(os.path.join(home_page_url, "robots.txt")) as response:
#    robots_txt_content = response.read().decode("utf-8")

# rp.parse(robots_txt_content)

# print(rp.can_fetch("*", BASE_URL))

time.sleep(3)

rp = RobotFileParser()
rp.set_url(os.path.join(home_page_url, "robots.txt"))
rp.read()

print(rp.can_fetch("*", BASE_URL))
