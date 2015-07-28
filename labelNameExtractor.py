#!/usr/bin/pypy

#list of tuples, labels[i][0] is the label, labels[i][1] is the property name
#currently requires the labels_en.nq file to be in the same directory
def load_labels():
    labels = []
    with open("labels_en.nq", "r") as f:
        counter = 0
        for line in f:
            name = line[len('<http://dbpedia.org/resource/'):line.find('>')]
            start_index = line.find('\"')+1
            end_index = line.find('\"', start_index)
            label = line[start_index:end_index]
            labels.append((label, name))
    return labels

def levenshtein(s, t):
        ''' From Wikipedia article; Iterative with two matrix rows. '''
        if s == t: return 0
        elif len(s) == 0: return len(t)
        elif len(t) == 0: return len(s)
        v0 = [None] * (len(t) + 1)
        v1 = [None] * (len(t) + 1)
        for i in range(len(v0)):
            v0[i] = i
        for i in range(len(s)):
            v1[0] = i + 1
            for j in range(len(t)):
                cost = 0 if s[i] == t[j] else 1
                v1[j + 1] = min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost)
            for j in range(len(v0)):
                v0[j] = v1[j]
        return v1[len(t)]

def binary_search(name, labels):
    lower_bound = 0
    upper_bound = len(labels)
    middle = 0
    found = False
    result = []
    while lower_bound <= upper_bound:
        middle = (lower_bound+upper_bound) // 2
        result.extend(check_neighbours(name, labels, middle))
        if labels[middle][0] < name:
            lower_bound = middle + 1
        elif labels[middle][0] > name:
            upper_bound = middle - 1
        else:
            break #full match
    return result

#checks the edit distance of 4 neighbours and the target index
def check_neighbours(name, labels, index):
    #check bounds of list
    start = (index - 2) if (index - 2) > 0 else 0
    end = (index + 2) if (index + 2) < (len(labels) - 1) else (len(labels) - 1)
    res = []
    edit_threshold = 3
    for x in range(start, end):
        if (levenshtein(name, labels[x][0]) <= edit_threshold):
            res.append(labels[x][1])
    return res


labels = load_labels()
labels.sort(key=lambda x: x[0])
reversed_labels = map(lambda x: (x[0][::-1], x[1]), labels)
reversed_labels.sort(key=lambda x: x[0])

while (True):
    name = raw_input("lets look for: ")
    if (name == "exit"):
        break
    result = binary_search(name, labels)
    result.extend(binary_search(name[::-1], reversed_labels))
    print set(result)
