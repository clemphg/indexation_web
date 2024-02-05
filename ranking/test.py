import json
import math
from main import tokenize

with open("title_pos_index.json") as f:
    index_title = json.load(f)


def compute_bm25(query, index, documents, metadata, b, k1):
    """Computes the bm25 score of each document for a specific query"""

    tokenized_query = tokenize(query)

    document_scores = {}

    for doc in documents:
        doc_id = doc['docId']
        title = doc['title']

        bm25 = 0
        for token in tokenized_query:
            if token in index.keys() and str(doc_id) in index[token].keys():
                print('ok')

                # compute inverse document frequency
                idf = math.log(len(documents)/len(index[token].keys()))

                # compute the frequency (count) of token in title of doc
                freq_tok_in_doc = index[token][str(doc_id)]['count']

                # fieldLen/avg(fieldLen)
                field_len = len(tokenize(title))
                avg_field_len = metadata['mean_nb_tokens_title']

                # compute bm25
                bm25 += idf*(freq_tok_in_doc*(k1+1))/(freq_tok_in_doc+k1*(1-b+b*field_len/avg_field_len))

        document_scores[doc_id] = bm25

    return document_scores


documents = [
    {
        'docId': 1,
        'title': "Des nouvelles très importantes sur la vie de nos amis les chiens"
    },
    {
        'docId': 2,
        'title': "J'ai de nouvelles chaussures vertes"
    },
    {
        'docId': 3,
        'title': "Les nouvelles vont vite dans cette ville traversée par des coulées vertes , très vertes"
    },
]

metadata = {
    'mean_nb_tokens_title': sum([len(tokenize(doc['title'])) for doc in documents])/len(documents)
}

index_title = {
    'des': {'1': {'count': 1}},
    'nouvelles': {'1': {'count': 1}, '2': {'count': 1}, '3': {'count': 1}},
    'vertes': {'2': {'count': 1}, '3': {'count': 3}}
}


query = 'nouvelles vertes'

# params bm25
b = 0.75
k1 = 1.2

print(compute_bm25(query, index_title, documents, metadata, b, k1))