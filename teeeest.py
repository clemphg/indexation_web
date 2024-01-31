import json


#with open('index/title.pos_index.json') as f:
#    index = json.load(f)

#print(index)

d = {"!": {2: [9], 9: [19], 47: [9]},"'": {97: [24]}, "''": {68: [9], 82: [16], 91: [19], 96: [22], 97: [41]}}

json_str = "{\n"
for token, values in sorted(d.items()):
    if isinstance(values, dict):
        val_str = "{"
        for docId, pos in sorted(values.items()):
            val_str += f'"{docId}": {pos}, '
        val_str = val_str.rstrip(", ") + "}"
        json_str += f'    "{token}": {val_str},\n'
    else:
        json_str += f'    "{token}": {values},\n'
json_str = json_str.rstrip(",\n") + "\n"+"}"

print(json_str)