#!/usr/bin/python
# Script for sqlite lookupfrom crossweb dataset
# Usage: ./lookup-service-sqlite.py labels.db

from SPARQLWrapper import SPARQLWrapper, JSON
import sqlite3
import sys

from flask import *
app = Flask(__name__)

db = "labels.db"
dbpurl = 'http://dbpedia.ailao.eu:3030/dbpedia/query'


def queryWikipediaId(label):
    """ Convert the label to a pageId. """
    if label is None: return None
    # first, check if this is a redirect and traverse it
    retVal = queryWikipediaIdRedirected(label)
    if retVal is not None:
        return retVal
    sparql = SPARQLWrapper(dbpurl)
    sparql.setReturnFormat(JSON)
    sparql_query = '''
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT DISTINCT ?pageID WHERE {
    <http://dbpedia.org/resource/''' + label + '''> <http://dbpedia.org/ontology/wikiPageID> ?pageID .
} '''
    sparql.setQuery(sparql_query)
    res = sparql.query().convert()
    retVal = []
    for r in res['results']['bindings']:
        retVal.append(r['pageID']['value'])
    return retVal[0] if retVal else None


def queryWikipediaIdRedirected(label):
    """ Convert the label to a pageId, traversing redirect.s """
    if label is None: return None
    sparql = SPARQLWrapper(dbpurl)
    sparql.setReturnFormat(JSON)
    sparql_query = '''
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?pageID WHERE {
    <http://dbpedia.org/resource/''' + label + '''> <http://dbpedia.org/ontology/wikiPageRedirects> ?tgt .
    ?tgt <http://dbpedia.org/ontology/wikiPageID> ?pageID .
} '''
    sparql.setQuery(sparql_query)
    res = sparql.query().convert()
    retVal = []
    for r in res['results']['bindings']:
        retVal.append(r['pageID']['value'])
    return retVal[0] if retVal else None


@app.route('/search/<path:name>')  # Also supports ?addPageId=1
def web_search(name):
    print "searching " + name.encode('utf-8')
    global dataset
    result_list = search(name, addPageId=request.args.get('addPageId', False))
    print "found:"
    print result_list[:3]
    return jsonify(results=result_list[:3])


def search(name, addPageId=False):
    connection = sqlite3.connect(db)
    connection.text_factory = str
    with connection:
        cursor = connection.cursor()
        cursor.execute("SELECT label, probability, url from labels as l JOIN urls as u on l.url_id = u.id where label=?", (name,))
        sresult = cursor.fetchall()
        # TODO: canonLabel? change dist?
        result_list = []
        for r in sresult:
            result = {
                'matchedLabel': r[0],
                'canonLabel': r[2],
                'name': r[2],
                'dist': 0,
                'prob': r[1]
            }
            if addPageId:
                # We don't do this by default as YodaQA proper doesn't need
                # this.  However, some other auxiliary stuff also uses this
                # service and typically always needs the pageId rather than
                # a label, to follow up in Freebase or a Solr collection.
                result['pageId'] = queryWikipediaId(result['name'])
            result_list.append(result)
        return result_list


if __name__ == "__main__":
    db = sys.argv[1]
    app.run(port=5001, host='::', debug=False, use_reloader=False)
