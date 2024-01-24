from urllib.parse import urlparse

url = 'https://ensai.fr/international/partenaires-internationaux/'


p = urlparse(url)

print(p.scheme+"://"+p.netloc)