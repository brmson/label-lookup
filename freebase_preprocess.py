#!/usr/bin/pypy
# Pre-process the RDF datasets.
#
# Takes a pair of datasets
#   * (URL, has-a, label) triplets
#   * (URL, has-a, freebase_link) triplets
# and generates a new dataset of (label, URL, freebaseID, isCanonical) tuples,
# sorted by the label and the isCanonical flag indicating whether this is
# *not* a redirect.
#
# Usage: ./freebase_preprocess.py labels_en.tql transitive_redirects_en.ttl freebase_links_en.ttl sorted_fb_list.dat

import sys
from liblookup import ntfile


def save_to_file(labels, label_map, fb_map, redirect_map, list_filename):
    with open(list_filename, "w") as f:
        for label in labels:
            url = label_map[label]
            try:
                url = redirect_map[url]
                isCanon = False
            except KeyError:
                isCanon = True
            try:
                fb_id = fb_map[url]
            except KeyError:
                # no freebase id found!
                continue
            f.write("%s\t%s\t%s\t%d\n" % (label, url, fb_id, isCanon))


if __name__ == "__main__":
    labels_filename, redirects_filename, freebase_filename, list_filename = sys.argv[1:]

    print("loading labels")
    label_map = ntfile.load_literals(labels_filename, first=1)
    print("loading freebase IDs")
    fb_map = ntfile.load_fb_resources(freebase_filename)
    print("loading redirects")
    redirect_map = ntfile.load_resources(redirects_filename)
    labels = label_map.keys()
    print("saving to file")
    save_to_file(labels, label_map, fb_map, redirect_map, list_filename)
