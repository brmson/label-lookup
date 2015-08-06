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


def save_to_file(labels, label_map, id_map, list_filename):
    with open(list_filename, "w") as f:
        for label in labels:
            url = label_map[label]
            pageID = id_map[url]
            f.write("%s\t%s\t%s\n" % (label, url, pageID))


if __name__ == "__main__":
    labels_filename, pageIDs_filename, list_filename = sys.argv[1:]

    print "loading labels"
    label_map = ntfile.load_literals(labels_filename, first=1)
    print "loading IDs"
    id_map = ntfile.load_literals(pageIDs_filename)

    print "loading done, sorting"
    labels = sorted(label_map.keys())

    print "saving to file"
    save_to_file(labels, label_map, id_map, list_filename)
