import json

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

for doc in docs:
    print(doc)