import re
import json
import pandas as pd

import time

def tokenize(text):
    """Tokenizes a string (lowers+splits by whitespaces)"""
    text = re.sub(r' +', ' ', text)
    return text.lower().split(' ')


def filter_docs(index, query) -> list[int]:
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


def format_ranking_results(documents, ranking) -> list[dict]:

    formated_ranking = []

    for rank, docid in ranking.items():
        doc = [doc for doc in documents if doc['id']==docid][0]
        res = {'title': doc['title'],
               'url': doc['url']}
        formated_ranking.append(res)

    return formated_ranking

def linear_ranking(documents, index_title, index_content) -> dict:
    """Rank documents"""
    # only uses index to compute (info sur frequence and position of tokens)

    ranking = {} # rank: doc_id

    return ranking

with open('ranking/title_pos_index.json') as f:
    index_title = json.load(f)

with open('ranking/content_pos_index.json') as f:
    index_content = json.load(f)

query = "pourquoi erreur"

filtered_docs = filter_docs(index_title, query)
print(filtered_docs)


ranking = {}

tokenized_query = tokenize(query)

tokenized_query = [token for token in tokenized_query if token in index_title.keys()]

tokenized_query = list(set(tokenized_query))

work_token = {} # token: {docId: {position: [int], count: int}}

for token in tokenized_query:
    # keep token position and info for each doc
    work_token[token] = {int(docId): value for docId, value in index_title[token].items()
                         if int(docId) in filtered_docs}


work_doc = {} # docId: {token1: count, token2: count}
for docId in filtered_docs:
    work_doc[docId] = {token: work_token[token][docId]for token in tokenized_query}

# avec une comprésention de dictionnaire
#work_doc = {docId: {token: work_token[token][docId]['count'] for token in tokenized_query} 
#            for docId in filtered_docs}

# un score selon le compte de tokens (**2 pour donner plus d'importance à des docs où il y aurait plus d'occurences de ces tokens)
score_counts = {docId: sum([work_doc[docId][token]['count'] 
                            for token in tokenized_query])**2 
                for docId in filtered_docs}

# un score selon la position des tokens (+ils sont ordonnés plus le score est grand)
for key, val in work_doc.items():
    print(key, val)

d = {docId: [work_doc[docId][token]['positions'] for token in tokenized_query] for docId in filtered_docs}

# un score ordonnés ou non (nombre de fois ou un token de la query est avant le suivant dans le titre )
# tokens query = ['a', 'b', 'c']

# returns sum([pos_a<pos_b, pos_b<posc]) pour chaque doc
# if title = 'a c b'
score_o = {docId: sum([min(p1)<min(p2) for p1, p2 in zip(d[docId][:-1], d[docId][1:])]) for docId in filtered_docs}



# un score proche ou non (éventuellement décroissant)

# somme des scores
scores = {docId: score_counts[docId]+score_o[docId] for docId in filtered_docs}

for key, val in scores.items():
    print(key, val)



ranking = {0: 116,
       1: 4431,
       2: 10917}

# load documents as a list of dictionnaries, each with keys [url, id, title]
with open('ranking/documents.json') as f:
    documents = json.load(f)

formated_ranking = format_ranking_results(documents, ranking)

save_json(formated_ranking, 'sample.json')