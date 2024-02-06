# Lab web indexation [Index] - ENSAI 2024
Clémentine Phung [clementine.phung-ngoc@eleve.ensai.fr]

This `README.md` refers to lab 2 about indexing. Bonuses 1 (stemming) and 2 (positional index) were implemented, it is also possible to select the field on which we want to build the index (`title`, `content` or `h1`).

## Code

### Libraries
- **pandas** to store and manipulate the corpus.
- **nltk** to tokenize strings and stem tokens.

### Functions

- `preprocess(text:str, stem:bool, language:str) -> list[str]`: tokenizes a string and stems it if `stem=True`, in the specified language.
- `preprocess_data(data:pd.DataFrame, stem:bool, language:str) -> None`: processes the fields `title`, `content` and `h1` and adds three columns to the dataframe `data` with the preprocessing results.
- `compute_metadata(data:pd.DataFrame) -> dict`: computes some statistics about the corpus.
- `compute_inverted_index(data:pd.DataFrame, attribute:str, positional:bool) -> dict`: computes an inverted index on the field `attribute`, which can be positional if `positional=True`.
- `save_json(data:dict, filename:str, sort_keys:bool=True) -> None`: writes a dictionnary into a JSON file with indents for better readability of the data.
- `main() -> None`: parses arguments and runs the other functions to compute statistics about the corpus as well as the inverted index.

## Use

To run the code as explained, please place yourself in the `/index` folder.

Non positional index without stemming:
```
python3 main.py -i title.non_pos_index.json
```
Non positional index with stemming: 
```
python3 main.py -i mon_stemmer.title.non_pos_index.json -s True
```
Positional index without stemming:
```
python3 main.py -i title.pos_index.json -p True
```
All available options are listed and briefly explained in the documentation:
```
python3 main.py --help
```
```
usage: main.py [-h] [-c CORPUS] [-m METADATA] [-i INDEX] [-a {title,content,h1}] [-s {True,False}] [-p {True,False}] [-l {french,english}]

options:
  -h, --help            show this help message and exit
  -c CORPUS, --corpus CORPUS
                        Filename of corpus to create the index for, default 'crawled_urls.json'.
  -m METADATA, --metadata METADATA
                        Filename for metadata about the corpus, default 'metadata.json'.
  -i INDEX, --index INDEX
                        Filename for the computed inverted index, default 'inverted_index.json'.
  -a {title,content,h1}, --attribute {title,content,h1}
                        Attribute to create the index on, default 'title'.
  -s {True,False}, --stemming {True,False}
                        Whether or not to stem tokens, default False.
  -p {True,False}, --positional {True,False}
                        Whether or not to compute a positional index, default False.
  -l {french,english}, --language {french,english}
                        Main language of corpus, default 'french'.
```
