"""
main.py

to improve:
- find better tokenizer
- select the field on which we should build the index
- create function which tokenizes the fields title, content and h1
"""

import re
import argparse

import pandas as pd

# on peut utiliser les librairies qu'on veut pour tokenizer
# tokenizer (très basique, à améliorer)
def tokenizer(text):
    """Tokenizes a string (removes punctuation, splits by whitespaces)"""
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r' +', ' ', text)
    return text.lower().split(' ')

def compute_metadata(data):
    """Computes statistics about the corpus"""

    # nombre de tokens global et par champ
    nb_tokens_titles = [len(title) for title in data['title_tokenized']]
    nb_tokens_contents = [len(content) for content in data['content_tokenized']]
    nb_tokens_h1s = [len(h1) for h1 in data['h1_tokenized']]

    nb_tokens_global = sum(nb_tokens_titles)+sum(nb_tokens_contents)+sum(nb_tokens_h1s)

    metadata = {
        'nb_doc': len(data),
        'nb_tokens_title_total': sum(nb_tokens_titles),
        'nb_tokens_content_total': sum(nb_tokens_contents),
        'nb_tokens_h1_total': sum(nb_tokens_h1s),
        'nb_tokens_total': nb_tokens_global,
        'mean_nb_tokens_title': sum(nb_tokens_titles)/len(data),
        'mean_nb_tokens_content': sum(nb_tokens_contents)/len(data),
        'mean_nb_tokens_h1': sum(nb_tokens_h1s)/len(data),
        'mean_nb_tokens_doc': nb_tokens_global/len(data)
    }

    return metadata

def compute_inverted_index(data):
    """Computes simple inverted index"""
    # initialize simple inverted index dict[token] -> list[docs]
    inv_index = {}

    for idx, row in data.iterrows():
        for token in list(set(row['title_tokenized'])):
            if token in inv_index.keys():
                inv_index[token].append(idx)
            else:
                inv_index[token] = [idx]
    return inv_index


def save_json(data: dict, filename: str, sort_keys:bool=True) -> None:
    """Writes data into filename, sorts keys if asked to"""

    # generate formatted json string
    json_str = "{\n"
    if sort_keys:
        for token, values in sorted(data.items()):
            json_str += f'    "{token}": {values},\n'
    else:
        for token, values in data.items():
            json_str += f'    "{token}": {values},\n'
    json_str = json_str.rstrip(",\n") + "\n"+"}"

    # save the formatted json string to filename
    with open(filename, "w") as json_file:
        json_file.write(json_str)

    print(f"JSON file saved at: {filename}")

def main():

    # parsing arguments
    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--corpus", 
                        default='crawled_urls.json', 
                        help="Filename of corpus to create the index for, default 'crawled_urls.json'.",
                        type=str)
    parser.add_argument("-m", "--metadata", 
                        default='metadata.json', 
                        help="Filename for metadata about the corpus, default 'metadata.json'.",
                        type=str)
    parser.add_argument("-i", "--index", 
                        default='inverted_index.json', 
                        help="Filename for the computed inverted index, default 'inverted_index.json'.",
                        type=str)
    
    args = parser.parse_args()

    # load data
    crawled_urls = pd.read_json(args.corpus, encoding='utf-8')

    # tokenize text fields and add them to the dataframe
    crawled_urls['title_tokenized'] = [tokenizer(title) for title in crawled_urls['title']]
    crawled_urls['content_tokenized'] = [tokenizer(content) for content in crawled_urls['content']]
    crawled_urls['h1_tokenized'] = [tokenizer(h1) for h1 in crawled_urls['h1']]

    metadata = compute_metadata(crawled_urls)
    save_json(metadata, args.metadata, sort_keys=False)

    inverted_index = compute_inverted_index(crawled_urls)
    save_json(inverted_index, args.index)


if __name__=="__main__":
    
    main()

    # python3 main.py -i title.non_pos_index.json
