"""
main.py
"""

import re
import json
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

def linear_ranking(doc_ids, index_title, index_content) -> dict:
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

    # loading content positional index
    with open(args.index_content) as f:
        index_content = json.load(f)

    # setting the query 
    query = args.query

    # filtering documents containing all of the query tokens 
    filtered_docs = filter_docs(index_title, query)

    # ranking the documents
    ranking = linear_ranking(filtered_docs, index_title, index_content)

    # load document info as a list of dictionnaries, each with keys [url, id, title]
    with open(args.document) as f:
        documents = json.load(f)

    # extract title and url of ranked documents
    formated_ranking = format_ranking_results(documents, ranking)

    # save results as a list of dictionnaries, each with keys [title, url]
    save_json(formated_ranking, 'sample.json')


if __name__=="__main__":
    
    main()