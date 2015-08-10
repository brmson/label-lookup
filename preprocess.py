#!/usr/bin/pypy
# Pre-process the RDF datasets.
#
# Takes a pair of datasets
#   * (URL, has-a, label) triplets
#   * (URL, has-a, pageID) triplets
# and generates a new dataset of (label, URL_subset, pageID) triplets
# sorted by the label.
# and generates a new dataset of (label, URL, pageID, isCanonical) tuples,
# sorted by the label and the isCanonical flag indicating whether this is
# *not* a redirect.
#
# Usage: ./preprocess.py labels_en.nt page_ids_en.nt redirects_transitive_en.nt sorted_list.dat

import sys
from liblookup import ntfile


def save_to_file(labels, label_map, id_map, redirect_map, list_filename):
    with open(list_filename, "w") as f:
        for label in labels:
            url = label_map[label]
            try:
                url = redirect_map[url]
                isCanon = False
            except KeyError:
                isCanon = True
            try:
                pageID = id_map[url]
            except KeyError:
                # We may follow a redirect from general namespace to specific
                # one, e.g. Wikipedia:, but we don't have pageIDs for these.
                # This is junk anyway, skip it completely.
                continue
            f.write("%s\t%s\t%s\t%d\n" % (label, url, pageID, isCanon))


if __name__ == "__main__":
    labels_filename, pageIDs_filename, redirects_filename, list_filename = sys.argv[1:]

    print "loading labels"
    label_map = ntfile.load_literals(labels_filename, first=1)
    print "loading IDs"
    id_map = ntfile.load_literals(pageIDs_filename)
    print "loading redirects"
    redirect_map = ntfile.load_resources(redirects_filename)

    print "loading done, sorting"
    labels = label_map.keys()
    labels.sort(key=lambda x: x.lower())

    print "saving to file"
    save_to_file(labels, label_map, id_map, redirect_map, list_filename)
