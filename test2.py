
a = [[1],[2],[1,5,8],[4],[5],[6]]

print(a[:-1])
print(a[1:])

print([min(e1)<min(e2) for e1, e2 in zip(a[:-1], a[1:])])


string = " Il fait beau "

print(string.strip().split(' '))