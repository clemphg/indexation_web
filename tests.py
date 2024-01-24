from urllib.robotparser import RobotFileParser
import os

base_url = 'https://ensai.fr/'

rp = RobotFileParser()
rp.set_url("https://ensai.fr/robots.txt")
rp.read()
print(rp.can_fetch("*", "https://ensai.fr/wp-login.php"))

