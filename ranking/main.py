"""
main.py
"""

import re
import json
import math
import argparse

def tokenize(text):
    """Tokenizes a string (lowers+splits by whitespaces)"""
    text = re.sub(r' +', ' ', text)
    return text.lower().split(' ')

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

def linear_ranking(query, filtered_docs, index, weights):
    """Ranks documents based on a linear ranking score."""

    # Tokenize the query
    query_tokens = query.lower().split()

    # Initialize a dictionary to store document scores
    document_scores = {}


    # Calculate scores for each document
    for document in filtered_docs:
        doc_id = document['id']
        title = document['title'].lower()

        # Initialize score
        score = 0

        # Feature 1: Number of tokens in title document
        num_tokens_feature = len(title.split())
        score += weights['num_tokens'] * 1/num_tokens_feature

        # Feature 2: Importance based on token positions
        for query_token in query_tokens:
            if query_token in index and doc_id in index[query_token]:
                positions = index[query_token][doc_id]['positions']
                importance_feature = sum([1 / math.sqrt(pos) for pos in positions])
                score += weights['importance'] * importance_feature

        # Feature 3: Score on whether tokens are in the same order in the query and the title

        # Save the score for the document
        document_scores[doc_id] = score

    tokenized_query = [token for token in tokenize(query) if token in index.keys()]
    tokenized_query = list(set(tokenized_query))

    work_token = {} # token: {docId: {position: [int], count: int}}

    filtered_docs_ids = [doc['id'] for doc in filtered_docs]

    for token in tokenized_query:
        # keep token position and info for each doc
        work_token[token] = {int(docId): value for docId, value in index[token].items()
                            if int(docId) in filtered_docs_ids}

    work_doc = {} # docId: {token1: count, token2: count}
    for docId in filtered_docs_ids:
        work_doc[docId] = {token: work_token[token][docId]for token in tokenized_query}

    # avec une comprésention de dictionnaire
    #work_doc = {docId: {token: work_token[token][docId]['count'] for token in tokenized_query} 
    #            for docId in filtered_docs_ids}

    # un score selon le compte de tokens (**2 pour donner plus d'importance à des docs où il y aurait plus d'occurences de ces tokens)
    score_counts = {docId: sum([work_doc[docId][token]['count'] 
                                for token in tokenized_query])**2 
                    for docId in filtered_docs_ids}

    d = {docId: [work_doc[docId][token]['positions'] for token in tokenized_query] for docId in filtered_docs_ids}

    # un score ordonnés ou non (nombre de fois ou un token de la query est avant le suivant dans le titre )
    # tokens query = ['a', 'b', 'c']

    # returns sum([pos_a<pos_b, pos_b<posc]) pour chaque doc
    # if title = 'a c b'
    score_o = {docId: sum([min(p1)<min(p2) for p1, p2 in zip(d[docId][:-1], d[docId][1:])]) for docId in filtered_docs_ids}

    document_scores = {docId: score+score_o[docId] for docId, score in document_scores.items()}

    # Rank documents based on scores
    ranked_documents = dict(sorted(document_scores.items(), key=lambda x: x[1], reverse=True))

    ranks = {rank+1: docId for rank, docId in zip(list(range(len(filtered_docs))), ranked_documents.keys())}

    # Return the ranked documents
    return ranks

def format_ranking_results(documents, ranking) -> list[dict]:
    """Formats the ranking results into string for parsed json export"""

    formated_ranking = []

    for _, docid in ranking.items():
        doc = [doc for doc in documents if doc['id']==docid][0]
        res = {'title': doc['title'],
               'url': doc['url']}
        formated_ranking.append(res)

    return formated_ranking

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

def main():

    # parsing arguments
    parser = argparse.ArgumentParser()

    parser.add_argument("query",
                        help="query for ranking.",
                        type=str)
    parser.add_argument("-it", "--index_title", 
                        default='title_pos_index.json', 
                        help="filename of title positional index, default 'title_pos_index.json'",
                        type=str)
    parser.add_argument("-ic", "--index_content", 
                        default='content_pos_index.json', 
                        help="filename of content positional index, default 'content_pos_index.json'",
                        type=str)
    parser.add_argument("-d", "--documents", 
                        default='documents.json', 
                        help="filename of documents list, default 'documents.json'",
                        type=str)
    parser.add_argument("-r", "--results", 
                        default='results.json', 
                        help="filename for ranking results, default 'results.json'",
                        type=str)
    
    args = parser.parse_args()

    # loading title positional index
    with open(args.index_title) as f:
        index_title = json.load(f)

    # load document info as a list of dictionnaries, each with keys [url, id, title]
    with open(args.documents) as f:
        documents = json.load(f)
    print(f"Number of documents: {len(documents)}")

    # setting the query 
    query = args.query

    # filtering documents containing all of the query tokens 
    filtered_docs_ids = filter_docs(index_title, query)
    print(f"Number of documents kept by the filter: {len(filtered_docs_ids)}")

    # selecting documents whos ids where kept through the filter
    filtered_docs = [doc for doc in documents if doc['id'] in filtered_docs_ids]

    # ranking the documents
    weights = {"num_tokens": 0.5, "importance": 1.0}
    ranking = linear_ranking(query, filtered_docs, index_title, weights)

    # extract title and url of ranked documents
    formated_ranking = format_ranking_results(documents, ranking)

    # save results as a list of dictionnaries, each with keys [title, url]
    save_json(formated_ranking, 'sample.json')


if __name__=="__main__":
    
    main()
    # example: python3 main.py 'pourquoi erreur'