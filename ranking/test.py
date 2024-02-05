import json
import re

a = [[1],[2],[1,5,8],[4],[5],[6]]

print(a[:-1])
print(a[1:])

print([min(e1)<min(e2) for e1, e2 in zip(a[:-1], a[1:])])


string = " Il fait beau "

print(string.strip().split(' '))


with open('ranking/documents.json') as f:
    documents = json.load(f)
    
l1 = [4307, 11479, 11561]

# l1=[1343, 3669, 13295]

# l1=[3883, 3884, 5385, 5386]

l1=[3979, 4912, 7842, 9130, 9691, 10755, 12731, 12981, 13007, 13151]

docs = [doc for doc in documents if doc['id'] in l1]

#for doc in docs:
#    print(doc)

#from nltk.corpus import stopwords
#stopwords = set(stopwords.words('english'))
#print(stopwords)

def tokenize(text):
    """Tokenizes a string (lowers+splits by whitespaces)"""
    text = re.sub(r' +', ' ', text)
    return text.lower().split(' ')

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


index = {"hello": {'1':{}, '2':{}}, 
         'world': {'3':{}, '2':{}},
         '!': {'1':{}, '4':{}}}

query = 'hello world'
print(filter_docs(index, query, 'OR'))