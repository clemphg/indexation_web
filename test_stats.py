import re
import time
import pandas as pd

crawled_urls = pd.read_json('crawled_urls.json', encoding='utf-8')
#print(crawled_urls.info())

# on peut utiliser les librairies qu'on veut pour tokenizer
# tokenizer (très basique, à améliorer)
def tokenizer(text):
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r' +', ' ', text)
    return text.lower().split(' ')

# COMPUTE STATS (on fait les stats qu'on veut)

# nombre de documents
print(f"Nombre de documents: {len(crawled_urls)}")




metadata = {}

# WRITING stats INTO JSON (with proper indentation)
file_path = "metadata.json"

# generate formatted json string
json_str = "{\n"
for token, values in sorted(metadata.items()):
    json_str += f'    "{token}": {values},\n'
json_str = json_str.rstrip(",\n") + "\n"+"}"

# Save the formatted JSON string to a file
with open(file_path, "w") as json_file:
    json_file.write(json_str)

print(f"JSON file saved at: {file_path}")