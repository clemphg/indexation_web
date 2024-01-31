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

# tokenize all fields
crawled_urls['title_tokenized'] = [tokenizer(title) for title in crawled_urls['title']]
crawled_urls['content_tokenized'] = [tokenizer(content) for content in crawled_urls['content']]
crawled_urls['h1_tokenized'] = [tokenizer(h1) for h1 in crawled_urls['h1']]

# COMPUTE STATS (on fait les stats qu'on veut)

# nombre de documents
print(f"Nombre de documents: {len(crawled_urls)}")

# nombre de tokens global et par champ
nb_tokens_titles = [len(title) for title in crawled_urls['title_tokenized']]
nb_tokens_contents = [len(content) for content in crawled_urls['content_tokenized']]
nb_tokens_h1s = [len(h1) for h1 in crawled_urls['h1_tokenized']]

nb_tokens_global = sum(nb_tokens_titles)+sum(nb_tokens_contents)+sum(nb_tokens_h1s)

# moyenne du nombre de tokens par document (champ puis doc)
mean_nb_tokens_title = sum(nb_tokens_titles)/len(nb_tokens_titles)
mean_nb_tokens_content = sum(nb_tokens_contents)/len(nb_tokens_contents)
mean_nb_tokens_h1 = sum(nb_tokens_h1s)/len(nb_tokens_h1s)

metadata = {
    'nb_doc': len(crawled_urls),
    'nb_tokens_title_total': sum(nb_tokens_titles),
    'nb_tokens_content_total': sum(nb_tokens_contents),
    'nb_tokens_h1_total': sum(nb_tokens_h1s),
    'nb_tokens_total': nb_tokens_global,
    'mean_nb_tokens_title': sum(nb_tokens_titles)/len(crawled_urls),
    'mean_nb_tokens_content': sum(nb_tokens_contents)/len(crawled_urls),
    'mean_nb_tokens_h1': sum(nb_tokens_h1s)/len(crawled_urls),
    'mean_nb_tokens_doc': nb_tokens_global/len(crawled_urls)
}

# WRITING stats INTO JSON (with proper indentation)
file_path = "metadata.json"

# generate formatted json string
json_str = "{\n"
for token, values in metadata.items():
    json_str += f'    "{token}": {values},\n'
json_str = json_str.rstrip(",\n") + "\n"+"}"

# Save the formatted JSON string to a file
with open(file_path, "w") as json_file:
    json_file.write(json_str)

print(f"JSON file saved at: {file_path}")