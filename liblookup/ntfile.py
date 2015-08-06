"""
Utilities for loading .nt RDF triple files.
"""

def load_literals(nt_filename, first=0):
    """
    From an .nt file, produce a list of tuples with the last and first
    elements.

    We make some strong assumptions:
    * the first element is DBpedia resource
    * the middle element is always the same predicate (which we ignore)
    * the last element is a literal

    If the first parameter is 0, the first element in the tuple is the
    name (URL); if it's 1, it's the label.
    """
    tuples = []
    with open(nt_filename, "r") as f:
        next(f)  # a comment comes first
        for line in f:
            name = line[len('<http://dbpedia.org/resource/'):line.find('>')]
            l_start_index = line.find('\"')+1
            l_end_index = line.find('\"', l_start_index)
            l = line[l_start_index:l_end_index]
            if first == 0:
                tuples.append((name, l))
            else:
                tuples.append((l, name))
    return tuples
