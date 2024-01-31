# TP d'indexation web [Index] - ENSAI 2024
Clémentine Phung [clementine.phung-ngoc@eleve.ensai.fr]

Ce `README.md` correspond au TP2 sur les index.

## Généralités

## Utilisation

Pour faire tourner le code tel qu'expliqué, veuillez vous placer dans le dossier `/index`. 

Index de base demandé :
```
python3 main.py -i title.non_pos_index.json
```
Index non positionnel avec stemming : 
```
python3 main.py -i mon_stemmer.title.non_pos_index.json -s True
```
Index positionnel sans stemming :
```
python3 main.py -i title.pos_index.json -p True
``` 
