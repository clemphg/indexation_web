import re
import json
import pandas as pd

def tokenize(text):
    """Tokenizes a string (lowers+splits by whitespaces)"""
    text = re.sub(r' +', ' ', text)
    return text.lower().split(' ')

with open('ranking/title_pos_index.json') as f:
    index = json.load(f)

query = "erreur fatale"


def filter_docs(index, query) -> list[str]:
    """Filters documents having all of the query's tokens"""
    # maybe use title and content index for more results

    # tokenize the query
    tokenized_query = tokenize(query)

    # check if all query tokens are in index
    # if not ignore these tokens
    tokenized_query = [token for token in tokenized_query if token in index.keys()]

    # print info about ignored tokens

    docs = list(index[tokenized_query[0]].keys())
    for token in tokenized_query[1:]:
        # only keep documents which contain all the previous tokens
        docs = [int(doc) for doc in docs if str(doc) in index[token].keys()]
    
    return docs

def save_json(data: list, filename: str) -> None:
    """Writes data into filename as a list of dictionnaries"""

    # generate formatted json string
    json_str = "[\n"
    for doc in data:
        json_str += '    {'+f'"title": "{doc["title"]}",\n'
        json_str += f'     "url": "{doc["url"]}"'+'},\n'
    json_str = json_str.rstrip(",\n") + "\n"+"]"

    # save the formatted json string to filename
    with open(filename, "w") as json_file:
        json_file.write(json_str)

    print(f"JSON file saved at: {filename}")


print(filter_docs(index, query))

# load documents as a list of dictionnaries, each with keys [url, id, title]
with open('ranking/documents.json') as f:
    documents = json.load(f)

def linear_ranking() -> dict:
    """Rank documents"""
    # only uses index to compute (info sur frequence and position of tokens)

    ranking = {} # rank: doc_id

    return ranking


def format_ranking_results(documents, ranking) -> list[dict]:

    formated_ranking = []

    for rank, docid in ranking.items():
        doc = [doc for doc in documents if doc['id']==docid][0]
        res = {'title': doc['title'],
               'url': doc['url']}
        formated_ranking.append(res)

    return formated_ranking

ran = {0: 116,
       1: 4431,
       2: 10917}

fran = format_ranking_results(documents, ran)

for row in fran:
    print(row)

save_json(fran, 'sample.json')