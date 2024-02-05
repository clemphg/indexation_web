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

def get_stopwords(language: str) -> list[str]:
    """Stopwords list of a given language"""
    stopwords = set(stopwords.words(language))
    return stopwords

def filter_docs(index:dict, query:str, filter:str) -> list[str]:
    """Filters documents having all of the query's tokens"""
    # maybe use title and content index for more results

    # tokenize the query
    tokenized_query = tokenize(query)

    # check if all query tokens are in index
    # if not ignore these tokens
    tokenized_query = [token for token in tokenized_query if token in index.keys()]

    # print info about ignored tokens

    if filter=='OR':
        docs = []
        for token in tokenized_query:
            # only keep documents which contain at least one query token
            docs = list(set(docs) | set(int(doc) for doc in index[token].keys()))
    else: # default behaviour = 'AND'
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


    # compute scores for each document
    for document in filtered_docs:
        doc_id = document['id']
        title = document['title'].lower()

        # Initialize score
        score = 0

        # score 1: nb of query tokens in title
        tokenized_title = title.split()
        num_q_tokens_in_title = len([tok for tok in list(set(query_tokens)) if tok in tokenized_title])
        score += weights['num_q_tokens_in_title']*num_q_tokens_in_title

        # score 2: nb token of query in title/nb of tokens in title$
        num_tokens_in_title = len(tokenized_title)
        score += weights['prop_tokens'] * num_q_tokens_in_title/num_tokens_in_title

        l_positions = []
        for token in query_tokens:
            if token in index and doc_id in index[token]:
                positions = index[token][doc_id]['positions']
                l_positions.append(positions)

                # score 3: the closer tokens are to the beginning of a sentence, the bigger the weight
                importance_feature = sum([1 / math.sqrt(pos) for pos in positions])
                score += weights['position'] * importance_feature
        
        # score 4: nb of ordered pairs of tokens
        score += weights['order']*sum([min(p1)<min(p2) for p1, p2 in zip(l_positions[:-1], l_positions[1:])])

        # store score for the document
        document_scores[doc_id] = score

    # rank documents based on scores
    ranked_documents = dict(sorted(document_scores.items(), key=lambda x: x[1], reverse=True))
    ranks = {rank+1: docId for rank, docId in zip(list(range(len(filtered_docs))), ranked_documents.keys())}

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
    parser.add_argument("-f", "--filter",
                        default='AND',
                        help="filter for the documents according to the query.",
                        type=str,
                        choices=['AND', 'OR'])
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
    filtered_docs_ids = filter_docs(index_title, query, args.filter)
    print(f"Number of documents kept by the filter    : {len(filtered_docs_ids)}")
    print(f"Proportion of documents kept by the filter: {round(100*len(filtered_docs_ids)/len(documents),3)}%")


    # selecting documents whos ids where kept through the filter
    filtered_docs = [doc for doc in documents if doc['id'] in filtered_docs_ids]

    # ranking the documents
    weights = {"num_q_tokens_in_title": 1,
               "prop_tokens": 0.5,
               "position": 1.0,
               "order": 1}
    ranking = linear_ranking(query, filtered_docs, index_title, weights)

    # extract title and url of ranked documents
    formated_ranking = format_ranking_results(documents, ranking)

    # save results as a list of dictionnaries, each with keys [title, url]
    save_json(formated_ranking, args.results)


if __name__=="__main__":
    
    main()
    # example: python3 main.py 'pourquoi erreur'