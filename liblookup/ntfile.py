"""
Utilities for loading .nt RDF triple files.
"""

def load_literals(nt_filename, first=0):
    """
    From an .nt file, produce a dict mapping between the first and last
    elements.

    We make some strong assumptions:
    * the first element is DBpedia resource
    * the middle element is always the same predicate (which we ignore)
    * the last element is a literal

    If the @first parameter is 0, the key in the dict is the name (URL);
    if it's 1, the key is the label.
    """
    mapping = dict()
    with open(nt_filename, "r") as f:
        next(f)  # a comment comes first
        for line in f:
            name = line[len('<http://dbpedia.org/resource/'):line.find('>')]
            l_start_index = line.find('\"')+1
            l_end_index = line.find('\"', l_start_index)
            l = line[l_start_index:l_end_index]
            if first == 0:
                mapping[name] = l
            else:
                mapping[l] = name
    return mapping
