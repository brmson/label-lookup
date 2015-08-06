#!/usr/bin/pypy
# Pre-process the RDF datasets.
#
# Takes a pair of datasets
#   * (URL, has-a, label) triplets
#   * (URL, has-a, pageID) triplets
# and generates a new dataset of (label, URL_subset, pageID) triplets
# sorted by the label.
#
# Usage: ./preprocess.py labels_en.nt page_ids_en.nt sorted_list.dat

import sys


# list of tuples, labels[i][0] is the label which we use to search, labels[i][1] is the property name which we return
def load_labels(labels_filename):
    loaded_labels = []
    with open(labels_filename, "r") as f:
        next(f)
        for line in f:
            name = line[len('<http://dbpedia.org/resource/'):line.find('>')]
            label_start_index = line.find('\"')+1
            label_end_index = line.find('\"', label_start_index)
            label = line[label_start_index:label_end_index]
            loaded_labels.append((label, name))
    return loaded_labels


# XXX code duplication
# labels[i][0] is the property name and labels[i][1] is the pageID
def load_IDs(pageIDs_filename):
    loaded_IDs = []
    with open(pageIDs_filename, "r") as p:
        next(p)
        for line in p:
            pageID_name = line[len('<http://dbpedia.org/resource/'):line.find('>')]
            pageID_start_index = line.find('\"') + 1
            pageID_end_index = line.find('\"', pageID_start_index)
            pageID = line[pageID_start_index:pageID_end_index]
            loaded_IDs.append((pageID_name, pageID))
    return loaded_IDs


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
    labels = load_labels(labels_filename)
    print "loading IDs"
    ids = load_IDs(pageIDs_filename)

    print "loading done, starting sort"
    labels.sort(key=lambda x: x[0])
    ids.sort(key=lambda x: x[0])

    print "sorting done, merging"
    labels_and_ids = merge_tuple_lists(labels, ids)

    print "saving to file"
    save_to_file(list_filename)
