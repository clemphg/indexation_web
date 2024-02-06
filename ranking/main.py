"""
main.py
"""

import re
import json
import math
import argparse

from nltk.corpus import stopwords

def tokenize(text: str) -> list[str]:
    """Tokenizes a string (lowers+splits by whitespaces).
    
    Parameter
    ---------
    text: str
        String to tokenize
    
    Returns
    -------
    list[str]
        List of tokens
    """
    text = re.sub(r' +', ' ', text)
    return text.lower().split(' ')

def get_stopwords(language: str) -> list[str]:
    """Computes the list of stopwords in a given language

    Parameter
    ---------
    language: str
        Language of the corpus
    
    Returns
    -------
    list[str]
        List of stopwords in language
    """
    lstopwords = set(stopwords.words(language))
    return lstopwords

def compute_metadata(data: list[dict]) -> dict[str, float]:
    """Computes statistics about the corpus
    This is a lighter version of the compute_metadata of lab 2 on indexing.

    Parameter
    ---------
    data: list[dict]
        Corpus, each dictionnary being a document
    
    Return
    ------
    dict[str, float]
        Dictionnary containing some statistics about the corpus
    """

    # nombre de tokens par titre
    nb_tokens_titles = [len(tokenize(doc['title'])) for doc in data]

    metadata = {
        'nb_doc': len(data),
        'nb_tokens_title_total': sum(nb_tokens_titles),
        'mean_nb_tokens_title': sum(nb_tokens_titles)/len(data),
    }

    return metadata

def filter_docs(index:dict[str, dict], query:str, filter:str) -> list[int]:
    """Filters documents having all of the query's tokens
    
    Parameters
    ----------
    index: dict[str, dict]
        Positional index, each key is a token and the values are documents in which
        the token appears, with the positions and the count.
    query: str
        Query entered by user
    filter: str
        Type of filter to select documents according to whether they contains all of
        the query's tokens or at least one. Either 'AND' or 'OR'.
    
    Returns
    -------
    list[int]
        List of docIds which were filtered.
    """
    # tokenize the query
    tokenized_query = tokenize(query)

    # check if all query tokens are in index
    # if not ignore these tokens
    tokenized_query = [token for token in tokenized_query if token in index.keys()]

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

def linear_ranking(query:str, 
                   filtered_docs:list[dict], 
                   index:dict[str, dict], 
                   weights:dict[str, float],
                   metadata:dict[str, float],
                   language:str) -> dict[int, int]:
    """Ranks documents based on a linear ranking score.

    This score is a weighted sum of four different scores:
        - one based on the number of query tokens which are in the title
        - one based on the proportion of title tokens which are query tokens
        - one based on the position of query tokens in the title
        - one is the bm25 score
        - one is based on the number of pairs of adjacent tokens of the query which 
        are in the same order in the query and the title.

    All score are combined using weights to compute a final score.
    The weight associated to stopwords tokens can be set to a value between 0 and 1,
    1 being the same weight as non stopwords tokens. This allows to not consider as 
    much stopwords token compared to non stopwords tokens.

    Parameters
    ----------
    query: str
        Query entered by user
    filtered_docs: list[dict]
        List of documents corresponding to documents selected by the filter
    index: dict[str, dict]
        Positional index, each key is a token and the values are documents in which
        the token appears, with the positions and the count.
    weights: dict[str, float]
        Weights associated to each score and stopwords
    metadata: dict[str, float]
        Dictionnary of statistics computed about the corpus
    language: str
        Language of the corpus (e.g. 'french', 'english',...)

    Returns
    -------
    dict[int, int]
        Dictionnary with keys being the rank and the value the corresponding docId
    """
    # tokenize the query
    query_tokens = query.lower().split()

    # initialize a dictionary to store document scores
    document_scores = {}

    # stopwords list
    lstopwords = get_stopwords(language)

    # compute scores for each document
    for document in filtered_docs:
        doc_id = document['id']
        title = document['title'].lower()

        # Initialize score
        score = 0

        # score 1: nb of query tokens in title (stopwords don't count as much as non stopwords)
        tokenized_title = title.split()
        q_tokens_in_title = [tok for tok in list(set(query_tokens)) if tok in tokenized_title]
        num_q_tokens_in_title = sum([weights['stopwords'] if tok in lstopwords else 1 for tok in q_tokens_in_title])
        score += weights['num_q_tokens_in_title']*num_q_tokens_in_title

        # score 2: nb token of query in title/nb of tokens in title$
        num_tokens_in_title = sum([weights['stopwords'] if tok in lstopwords else 1 for tok in tokenized_title])
        score += weights['prop_tokens'] * num_q_tokens_in_title/num_tokens_in_title

        l_positions = []
        bm25 = 0
        for token in query_tokens:
            if token in index.keys() and str(doc_id) in index[token]:
                positions = index[token][str(doc_id)]['positions']
                l_positions.append(positions)

                # score 3: the closer tokens are to the beginning of a sentence, the bigger the weight
                # unless token is a stopword in which case we don't count it as much
                discount = weights['stopwords'] if token in lstopwords else 1
                pos_score = sum([discount / math.sqrt(pos+1) for pos in positions])
                score += weights['position'] * pos_score

                # score 4: bm25
                b= 0.75
                k1 = 1.2
                # compute inverse document frequency
                idf = math.log(metadata['nb_doc']/len(index[token].keys()))
                # compute the frequency (count) of token in title of doc
                freq_tok_in_doc = index[token][str(doc_id)]['count']
                # fieldLen/avg(fieldLen)
                field_len = len(tokenize(title))
                avg_field_len = metadata['mean_nb_tokens_title']
                bm25 += idf*(freq_tok_in_doc*(k1+1))/(freq_tok_in_doc+k1*(1-b+b*field_len/avg_field_len))

        
        score += weights['bm25'] * bm25
        
        # score 5: nb of ordered pairs of tokens
        score += weights['order']*sum([min(p1)<min(p2) for p1, p2 in zip(l_positions[:-1], l_positions[1:])])

        # store score for the document
        document_scores[doc_id] = score

    # rank documents based on scores
    ranked_documents = dict(sorted(document_scores.items(), key=lambda x: x[1], reverse=True))
    ranks = {rank+1: docId for rank, docId in zip(list(range(len(filtered_docs))), ranked_documents.keys())}

    return ranks

def format_ranking_results(documents: list[dict], ranking:dict[int, int]) -> list[dict]:
    """Create results dictionnary, taking ranked docIds and associating the 
    corresponding titles and urls.
    
    Parameters
    ----------
    documents: list[dict]
        Corpus of documents
    ranking: dict[int, int]
        Ranking returned by the linear_ranking function
    
    Returns
    -------
    list[dict]
        Ordered list (first element is the document with rank 1) of documents,
        each document is a dictionnary with its title and its URL.
    """
    formated_ranking = []

    for _, docid in ranking.items():
        doc = [doc for doc in documents if doc['id']==docid][0]
        res = {'title': doc['title'],
               'url': doc['url']}
        formated_ranking.append(res)

    return formated_ranking

def save_json(data: list[dict], filename: str) -> None:
    """Writes data into filename as a list of dictionnaries
    
    Parameters
    ----------
    data: list[dict]
        Ordered list of ranked documents returned by format_ranking_results
    filename: str
        File to which results should be saved
    
    Returns
    -------
    None
    """

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

def main() -> None:
    """Allows to use functions"""

    # parsing arguments
    parser = argparse.ArgumentParser()

    parser.add_argument("query",
                        help="query for ranking",
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
    parser.add_argument("-l", "--language", 
                        default='french', 
                        help="language of documents, to compute stopwords list",
                        type=str)
    
    args = parser.parse_args()

    # loading title positional index
    with open(args.index_title) as f:
        index_title = json.load(f)

    # load document info as a list of dictionnaries, each with keys [url, id, title]
    with open(args.documents) as f:
        documents = json.load(f)
    print(f"Number of documents: {len(documents)}")

    # compute metadata about the corpus
    metadata = compute_metadata(documents)

    # setting the query 
    query = args.query

    # filtering documents containing all of the query tokens 
    filtered_docs_ids = filter_docs(index_title, query, args.filter)
    print(f"Number of documents kept by the filter    : {len(filtered_docs_ids)}")
    print(f"Proportion of documents kept by the filter: {round(100*len(filtered_docs_ids)/len(documents),3)}%")


    # selecting documents whos ids where kept through the filter
    filtered_docs = [doc for doc in documents if doc['id'] in filtered_docs_ids]

    # setting weigths to compute the score in linear_ranking 
    weights = {"num_q_tokens_in_title": 1,
               "prop_tokens": 0.5,
               "position": 1.0,
               "order": 2,
               "stopwords": 0.2,
               "bm25": 1}

    # ranking the documents
    ranking = linear_ranking(query, 
                             filtered_docs, 
                             index_title, 
                             weights, 
                             metadata,
                             args.language)

    # extract title and url of ranked documents
    formated_ranking = format_ranking_results(documents, ranking)

    # save results as a list of dictionnaries, each with keys [title, url]
    save_json(formated_ranking, args.results)


if __name__=="__main__":
    
    main()
    # example: python3 main.py 'pourquoi erreur'