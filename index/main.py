"""
main.py

to improve:
- find better tokenizer
- select the field on which we should build the index
- create function which tokenizes the fields title, content and h1
"""

import argparse

#import nltk
#nltk.download('punkt')

import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer


def preprocess(text:str, stem:bool, language:str) -> list[str]:
    """Tokenizes and stems text"""
    processed_text = word_tokenize(text, language=language)
    if stem:
        stemmer = SnowballStemmer(language=language)
        processed_text = [stemmer.stem(token) for token in processed_text]
    return processed_text

def preprocess_data(data:pd.DataFrame, stem:bool, language:str) -> None:
    data['title_preprocessed'] = [preprocess(title, stem, language) for title in data['title']]
    data['content_preprocessed'] = [preprocess(content, stem, language) for content in data['content']]
    data['h1_preprocessed'] = [preprocess(h1, stem, language) for h1 in data['h1']]


def compute_metadata(data:pd.DataFrame) -> dict:
    """Computes statistics about the corpus"""

    # nombre de tokens global et par champ
    nb_tokens_titles = [len(title) for title in data['title_preprocessed']]
    nb_tokens_contents = [len(content) for content in data['content_preprocessed']]
    nb_tokens_h1s = [len(h1) for h1 in data['h1_preprocessed']]

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

def compute_inverted_index(data:pd.DataFrame, attribute:str, positional:bool) -> dict:
    """Computes simple inverted index"""
    inv_index = {}

    # simple inverted index token: list[docIds]
    if not positional:
        for idx, row in data.iterrows():
            for token in list(set(row[attribute+'_preprocessed'])):
                if token in inv_index.keys():
                    inv_index[token].append(idx)
                else:
                    inv_index[token] = [idx]
    
    # positional inverted index token: {docId: list[int]}
    else:
        for idx, row in data.iterrows():
            tokenized = row[attribute+'_preprocessed']
            for i in range(len(tokenized)):
                if tokenized[i] in inv_index.keys():
                    if idx in inv_index[tokenized[i]].keys():
                        inv_index[tokenized[i]][idx].append(i)
                    else:
                        inv_index[tokenized[i]][idx] = [i]
                else:
                    inv_index[tokenized[i]] = {idx: [i]}
    return inv_index


def save_json(data:dict, filename:str, sort_keys:bool=True) -> None:
    """Writes data into filename, sorts keys if asked to"""

    # generate formatted json string
    json_str = "{\n"
    if sort_keys:
        data = dict(sorted(data.items()))

    for token, values in data.items():
        if isinstance(values, dict):
            val_str = "{"
            for docId, pos in sorted(values.items()):
                val_str += f'"{docId}": {pos}, '
            val_str = val_str.rstrip(", ") + "}"
            json_str += f'    "{token}": {val_str},\n'
        else:
            json_str += f'    "{token}": {values},\n'
    json_str = json_str.rstrip(",\n") + "\n"+"}"

    # save the formatted json string to filename
    with open(filename, "w") as json_file:
        json_file.write(json_str)

    print(f"JSON file saved at: {filename}")

def main() -> None:

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
    parser.add_argument("-a", "--attribute", 
                        default='title', 
                        help="Attribute to create the index on, default 'title'.",
                        type=str,
                        choices=['title', 'content', 'h1']),
    parser.add_argument("-s", "--stemming", 
                        default=False, 
                        help="Whether or not to stem tokens, default False.",
                        type=bool,
                        choices=[True, False]),
    parser.add_argument("-p", "--positional", 
                        default=False, 
                        help="Whether or not to compute a positional index, default False.",
                        type=bool,
                        choices=[True, False]),
    parser.add_argument("-l", "--language", 
                        default='french', 
                        help="Main language of corpus, default 'french'.",
                        type=str,
                        choices=['french', 'english'])
    
    args = parser.parse_args()

    print(f"Creating a{' positional ' if args.positional else 'n '}inverted index on '{args.attribute}' for {args.corpus}...")

    # load data
    crawled_urls = pd.read_json(args.corpus, encoding='utf-8')

    # process text fields and add them to the dataframe
    preprocess_data(crawled_urls, args.stemming, args.language)

    # compute metadata and save to json
    metadata = compute_metadata(crawled_urls)
    save_json(metadata, args.metadata, sort_keys=False)

    # compute inverted index and save to json
    inverted_index = compute_inverted_index(crawled_urls, args.attribute, args.positional)
    save_json(inverted_index, args.index)


if __name__=="__main__":
    
    main()

    # non positional inverted index              : python3 main.py -i title.non_pos_index.json
    # non positional inverted index with stemming: python3 main.py -i mon_stemmer.title.non_pos_index.json -s True
    # positional inverted index                  : python3 main.py -i title.pos_index.json -p True
