#!/usr/bin/pypy
# Script for pseudo-fuzzy search in a list of labels

from flask import *
app = Flask(__name__)

edit_threshold = 3
neighbours_to_check = 2  # the checked amount is double, because we look n positions up and n positions down
labels_and_ids = []
reversed_labels = []


def load_from_file():
    res = []
    with open("sorted_list.dat", "r") as f:
        for line in f:
            tmp = line.split("\t")
            res.append((tmp[0], tmp[1], tmp[2]))
    return res


def levenshtein(s, t):
    ''' From Wikipedia article; Iterative with two matrix rows. '''
    # XXX this can be done better using numPy
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
    result = set()

    while lower_bound <= upper_bound:
        middle = (lower_bound+upper_bound) // 2
        result = result | (check_neighbours(name, labels, middle))
        if labels[middle][0] < name:
            lower_bound = middle + 1
        elif labels[middle][0] > name:
            upper_bound = middle - 1
        else:
            break  # full match
    return result


# checks the edit distance of 2n neighbours and the target index
def check_neighbours(name, labels, index):
    # check bounds of list
    global neighbours_to_check
    start = (index - neighbours_to_check) if (index - neighbours_to_check) > 0 else 0
    end = (index + neighbours_to_check) if (index + neighbours_to_check) < (len(labels) - 1) else (len(labels) - 1)
    res = set()
    global edit_threshold
    for x in range(start, end):
        if (levenshtein(name, labels[x][0]) <= edit_threshold):
            res.add((labels[x][1], labels[x][2]))
    return res


def init():
    global labels_and_ids
    global reversed_labels
    print "loading from file"
    labels_and_ids = load_from_file()
    print len(labels_and_ids)
    reversed_labels = map(lambda x: (x[0][::-1], x[1], x[2]), labels_and_ids)
    reversed_labels.sort(key=lambda x: x[0])
    print "init done"


@app.route('/search/<name>')
def search(name):
    print "searching " + name
    result = set(ice)
    result = result | binary_search(name, labels_and_ids)
    result = result | binary_search(name[::-1], reversed_labels)
    result_list = list(result)
    result_list.sort(key=lambda x: levenshtein(name, x[0]))
    print "found:"
    print result_list[:3]
    return jsonify(results=result_list[:3])


def web_init():
    init()
    app.run()


# TOOD: add remote threshold and neighbourcount setting
def interactive():
    init()
    while (True):
        result = set()
        name = raw_input("lets look for: ")
        if (name == "exit"):
            break
        if (name == "setNeighbours"):
            global neighbours_to_check
            next_num = int(input("current neighbour count is "+str(neighbours_to_check)+", please input new number "))
            neighbours_to_check = next_num
            continue
        if (name == "setThreshold"):
            global edit_threshold
            next_num = int(input("current edit threshold is "+str(edit_threshold)+", please input new number "))
            edit_threshold = next_num
            continue
        result = result | binary_search(name, labels_and_ids)
        result = result | (binary_search(name[::-1], reversed_labels))
        print list(result)
        print "now sorted and trimed"
        sorted_list = list(result)  # XXX When the result is found using reversed labels, we should also sort it in a reverse way
        sorted_list.sort(key=lambda x: levenshtein(name, x[0]))
        print sorted_list[:3]
    return


if __name__ == "__main__":
    # To use a more interactive console mode, change web_init() to interactive()
    web_init()
