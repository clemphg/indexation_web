"""
Computing metadata
"""
import re
import time
import pandas as pd

crawled_urls = pd.read_json('crawled_urls.json', encoding='utf-8')
#print(crawled_urls.info())

#crawled_urls = crawled_urls[0:5]

# nombre de documents
print(f"Nombre de documents: {len(crawled_urls)}")

def tokenizer(text):
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r' +', ' ', text)
    return text.lower().split(' ')

# initialize simple inverted index dict[token] -> list[docs]
inv_index = {}

start_time = time.time()
for idx, row in crawled_urls.iterrows():
    tokenized_title = tokenizer(row['title'])
    for token in tokenized_title:
        if token in inv_index.keys():
            inv_index[token].append(idx)
        else:
            inv_index[token] = [idx]

print(f"Index creation time: {round(time.time()-start_time)}s")

# WRITING INVERTED INDEX INTO JSON (with proper indentation)
file_path = "inverted_index.json"

# generate formatted json string
json_str = "{\n"
for token, values in sorted(inv_index.items()):
    json_str += f'    "{token}": {values},\n'
json_str = json_str.rstrip(",\n") + "\n"+"}"

# Save the formatted JSON string to a file
with open(file_path, "w") as json_file:
    json_file.write(json_str)

print(f"JSON file saved at: {file_path}")