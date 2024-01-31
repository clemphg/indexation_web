import json

with open('sample.json') as f:
    file = json.load(f)

print(type(file[0]))