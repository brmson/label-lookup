#!/usr/bin/pypy
# Pre-process the RDF datasets.
#
# Takes a pair of datasets
#   * (URL, has-a, label) triplets
#   * (URL, has-a, pageID) triplets
# and generates a new dataset of (label, URL_subset, pageID) triplets
# sorted by the label.
# and generates a new dataset of (label, pageID) tuples sorted by
# the label.
#
# Usage: ./preprocess.py labels_en.nt page_ids_en.nt sorted_list.dat

import sys
from liblookup import ntfile


def binary_retrieve(name, ids):
    lower_bound = 0
    upper_bound = len(ids) - 1
    middle = 0
    while lower_bound <= upper_bound:
        middle = (lower_bound + upper_bound) // 2
        if ids[middle][0] < name:
            lower_bound = middle + 1
        elif ids[middle][0] > name:
            upper_bound = middle - 1
        else:
            return ids[middle][1]
    return -1


# finds a wikipedia ID for each label
# list[x][0] is the label we use to search, list[x][1] is the name to return and list[x][2] is the wikiID
def merge_tuple_lists(label_list, ID_list):
    result_list = []
    skipped = 0
    print str(len(label_list))
    print str(len(ID_list))
    for x in range(0, len(label_list)):
        nextID = binary_retrieve(label_list[x][1], ID_list)
        if(nextID != -1):
            result_list.append((label_list[x][0], label_list[x][1], nextID))
        else:
            skipped = skipped + 1
    percentage = (skipped/float(len(label_list)))*100
    print "skipped: " + str(skipped) + ", " + str(percentage) + "% "
    return result_list


def save_to_file(list_filename):
    with open(list_filename, "w") as f:
        for x in range(0, len(labels_and_ids)):
            f.write(labels_and_ids[x][0] + "\t" + labels_and_ids[x][1] + "\t" + labels_and_ids[x][2] + "\n")


if __name__ == "__main__":
    labels_filename, pageIDs_filename, list_filename = sys.argv[1:]

    print "loading labels"
    labels = ntfile.load_literals(labels_filename, first=1)
    print "loading IDs"
    ids = ntfile.load_literals(pageIDs_filename)

    print "loading done, starting sort"
    labels.sort(key=lambda x: x[0])
    ids.sort(key=lambda x: x[0])

    print "sorting done, merging"
    labels_and_ids = merge_tuple_lists(labels, ids)

    print "saving to file"
    save_to_file(list_filename)
