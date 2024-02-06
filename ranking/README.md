# Lab web ranking [Index] - ENSAI 2024
Clémentine Phung [clementine.phung-ngoc@eleve.ensai.fr]

This `README.md` refers to lab 3 about document ranking. All bonuses where implemented.

## Code

### Libraries
- **re** to tokenize by splitting at each whitespaces.
- **nltk** to get a list of stopwords.
- **json** to load and dump json files.

### Functions

#### Overview

- `tokenize(text: str) -> list[str]`: tokenizes a string.
- `get_stopwords(language: str) -> list[str]`: returns the list of stopwords in a given language.
- `compute_metadata(data: list[dict]) -> dict[str, float]`: computes some statistics about the corpus (number of documents, average number of tokens in titles).
- `filter_docs(index:dict[str, dict], query:str, filter:str) -> list[int]`: filters documents containing all of the query's tokens in their titles if filter is `AND`, or at least one if filter is `OR`.
- `linear_ranking(query:str, 
                   filtered_docs:list[dict], 
                   index:dict[str, dict], 
                   weights:dict[str, float],
                   metadata:dict[str, float],
                   language:str) -> dict[int, int]`: ranks filtered documents according to a linear ranking score.
- `format_ranking_results(documents: list[dict], ranking:dict[int, int]) -> list[dict]`: creates the results dictionnary that will be saved, taking ranked document ids and associating the corresponding titles and urls.
- `save_json(data: list[dict], filename: str) -> None`: writes a dictionnary into a JSON file with indents for better readability of the data.
- `main() -> None`: parses arguments and runs functions to compute the ranking.

#### Computation of the linear ranking scores

This score is a weighted sum of four different scores:
- the first one is based on the number of query tokens which are in the title,
- the second one is based on the proportion of title tokens which are query tokens (the higher the proportion is the higher the score is),
- the third one is based on the position of query tokens in the title (the closest query tokens are to the beginning of the title, the higher the score is),
- the fourth one is the **bm25 score**,
- the last score is based on the number of pairs of adjacent tokens of the query which are in the same order in the query and the title (e.g. if the query is `'tokenize strings python'` and the title is `'this python function allows to tokenize strings'`, then this score will be 1 since `'tokenize'` is before `'strings'` but `'string'` is not before `'python'` in the title).

All score are combined using weights to compute the final score. The weights dictionnary is set as:
```python
weights = {"num_q_tokens_in_title": 1,
           "prop_tokens": 0.5,
           "position": 1.0,
           "order": 2,
           "stopwords": 0.2,
           "bm25": 1}
```
The weight associated to **stopwords** tokens can be set to a value between 0 and 1, 1 being the same weight as non stopwords tokens. This allows to not consider as much stopwords token compared to non stopwords tokens when computing the scores.

## Use

To run the code as explained, please place yourself in the `/ranking` folder. 

To try the functions, you could run the following command for instance, it computes the ranking for the query `'pourquoi erreur'` with all the default parameters:
```
python3 main.py 'pourquoi erreur'
```
All available options are listed and briefly explained in the documentation:
```
python3 main.py --help
```
```
usage: main.py [-h] [-f {AND,OR}] [-it INDEX_TITLE] [-ic INDEX_CONTENT] [-d DOCUMENTS] [-r RESULTS] [-l LANGUAGE] query

positional arguments:
  query                 query for ranking

options:
  -h, --help            show this help message and exit
  -f {AND,OR}, --filter {AND,OR}
                        filter for the documents according to the query.
  -it INDEX_TITLE, --index_title INDEX_TITLE
                        filename of title positional index, default 'title_pos_index.json'
  -ic INDEX_CONTENT, --index_content INDEX_CONTENT
                        filename of content positional index, default 'content_pos_index.json'
  -d DOCUMENTS, --documents DOCUMENTS
                        filename of documents list, default 'documents.json'
  -r RESULTS, --results RESULTS
                        filename for ranking results, default 'results.json'
  -l LANGUAGE, --language LANGUAGE
                        language of documents, to compute stopwords list
```
