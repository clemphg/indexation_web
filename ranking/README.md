# Lab web ranking [Index] - ENSAI 2024
Clémentine Phung [clementine.phung-ngoc@eleve.ensai.fr]

This `README.md` refers to lab 3 about ranking.

## Code

### Libraries
- **json** to load and dump json files.
- **nltk** to tokenize strings and stem tokens.

### Functions

- `tokenize(text:str) -> list[str]`: tokenizes a string.
- `filter_docs(index, query) -> list[int]`: filters documents containing all of the query's tokens in their titles.
- `linear_ranking(query, filtered_docs, index, weights)`: ranks filtered documents based on a linear ranking score.
- `format_ranking_results(documents, ranking) -> list[dict]`: creates the results dictionnary that will be saved.
- `save_json(data: list, filename: str) -> None`: writes a dictionnary into a JSON file with indents for better readability of the data.
- `main() -> None`: parses arguments and runs the other functions to compute statistics about the corpus as well as the inverted index.

## Use

To run the code as explained, please place yourself in the `/ranking` folder.

Example:
```
python3 main.py 'pourquoi erreur'
```
All available options are listed and briefly explained in the documentation:
```
python3 main.py --help
```
```

```
