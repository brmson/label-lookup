#!/usr/bin/pypy
# Script for pseudo-fuzzy search in a list of labels
#
# Usage: ./lookup-service.py sorted_list.dat

import sys

from flask import *
app = Flask(__name__)

edit_threshold = 3
neighbours_to_check = 2  # the checked amount is double, because we look n positions up and n positions down


def levenshtein(s, t):
    ''' From Wikipedia article; Iterative with two matrix rows. '''
    # First, make things case-insensitive.
    # XXX: We should give some *small* penalty to case differences.
    s = s.lower()
    t = t.lower()

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
            res.add(labels[x])
    return res


def binary_search(name, labels):
    lower_bound = 0
    upper_bound = len(labels)
    middle = 0
    result = set()

    while lower_bound <= upper_bound:
        middle = (lower_bound+upper_bound) // 2
        result = result | (check_neighbours(name, labels, middle))
        if labels[middle][0].lower() < name:
            lower_bound = middle + 1
        elif labels[middle][0].lower() > name:
            upper_bound = middle - 1
        else:
            break  # full match
    return result


class Dataset:
    """
    Holding container for the mappings we query - from labels to URLs
    and from URLs to pageIDs.
    """
    def __init__(self, labels, id_map, canon_label_map):
        self.labels = labels
        self.reversed_labels = map(lambda x: (x[0][::-1], x[1]), labels)
        self.reversed_labels.sort(key=lambda x: x[0])
        self.id_map = id_map
        self.canon_label_map = canon_label_map

    @staticmethod
    def load_from_file(list_filename):
        print('loading labels')
        labels = []
        id_map = dict()
        canon_label_map = dict()
        with open(list_filename, "r") as f:
            for line in f:
                label, url, pageID, isCanon = line.rstrip().split("\t")
                labels.append((label, url))
                id_map[url] = pageID
                if bool(int(isCanon)):
                    canon_label_map[url] = label
        print len(labels)

        return Dataset(labels, id_map, canon_label_map)

    def search(self, name):
        name = name.lower()
        result = set()
        result = result | binary_search(name, self.labels)
        result = result | set([(r[0][::-1], r[1]) for r in binary_search(name[::-1], self.reversed_labels)])
        result_list = [{
                'matchedLabel': r[0],
                'canonLabel': self.canon_label_map[r[1]],
                'name': r[1],
                'pageID': self.id_map[r[1]],
                'dist': levenshtein(name, r[0])
            } for r in result]
        result_list.sort(key=lambda x: x['dist'])
        return result_list


@app.route('/search/<name>')
def web_search(name):
    print "searching " + name
    global dataset
    result_list = dataset.search(name)
    print "found:"
    print result_list[:3]
    return jsonify(results=result_list[:3])


def web_init(list_filename):
    global dataset
    dataset = Dataset.load_from_file(list_filename)
    app.run(port=5000, host='0.0.0.0', debug=True, use_reloader=False)


# TOOD: add remote threshold and neighbourcount setting
def interactive(list_filename):
    global dataset
    dataset = Dataset.load_from_file(list_filename)
    while (True):
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
        sorted_list = dataset.search(name)
        print sorted_list[:3]
    return


if __name__ == "__main__":
    list_filename = sys.argv[1]
    # To use a more interactive console mode, change web_init(...) to
    # interactive(...)
    web_init(list_filename)