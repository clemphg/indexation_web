import json
import math
from main import tokenize

with open("title_pos_index.json") as f:
    index_title = json.load(f)

query = 'pourquoi erreur'
documents = []
metadata = {}

# params bm25
b = 0.75
k1 = 1.2

def compute_bm25(query, documents, metadata, b, k1):
    """Computes the bm25 score of each document for a specific query"""

    tokenized_query = tokenize(query)

    document_scores = {}

    for doc in documents:
        doc_id = int(doc['docId'])
        title = doc['title']

        bm25 = 0
        for token in tokenized_query:
            if token in index_title.keys() and doc_id in token.keys():

                # compute inverse document frequency
                idf = math.log(len(documents)/len(index_title[token].keys()))

                # compute the frequency (count) of token in title of doc
                freq_tok_in_doc = index_title[token][doc_id]['count']

                # fieldLen/avg(fieldLen)
                field_len = len(tokenize(title))
                avg_field_len = metadata['mean_nb_tokens_title']

                # compute bm25
                bm25 += idf*(freq_tok_in_doc*(k1+1))/(freq_tok_in_doc+k1*(1-b+b*field_len/avg_field_len))

        document_scores[doc_id] = bm25

    return document_scores
