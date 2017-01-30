#!/usr/bin/python
# Script for sqlite lookupfrom crossweb dataset
# Usage: ./lookup-service-sqlite.py labels.db

import sqlite3
import sys
import urllib2

from flask import *
app = Flask(__name__)

db = "fb_db.db"

def generate_ngrams(text, n=5):
    tokens = text.strip().split(' ')
    new_list = [a for a in (list(zip(*[tokens[i:] for i in range(k)])) for k in range(1,n+1))]
    new_list.reverse()
    return [e for l in new_list for e in l]

def process_results(result_list):
    new_list = []
    for results in result_list:
        i = 0.0
        for result in results['results'][0]:
            i += result['prob']
        i = i/len(results['results'][0])
        if (i > 0.8):
            new_list.append(results)
    return new_list

@app.route('/search/<path:name>')  # Also supports ?ngrams=0
def web_search(name):
    # look for ngram or look just for the whole string
    ngrams = request.args.get('ngrams', False)
    top_n = request.args.get('topn', 3)
    result_list = []
    if ngrams:
        #for ngram_list in generate_ngrams(name):
        ngram_list = generate_ngrams(name)
        # for ngram in ngram_list:
        while len(ngram_list) != 0:
            ngram = ngram_list[0]
            print('looking for:', ngram)
            response = search(" ".join(ngram))
            # if len(response['results'][0]) > 0:
            if len(response) > 0:
                ls = generate_ngrams(" ".join(ngram),len(ngram))
                for l in ls:
                    if l in ngram_list:
                        ngram_list.remove(l)
                result_list.append(response)
            if ngram in ngram_list:
                ngram_list.remove(ngram)
        #result_list = process_results(result_list)
    else:
        print('looking for:', name)
        result_list.append(search(name))
    print(result_list)
    return jsonify(results=result_list[:top_n])


def search_remote(name):
    response = urllib2.urlopen('http://docker.alquistai.com:5001/search/' + name)
    result = response.read()
    html = json.loads(result)

    return html

def search(name):
    name = name.lower()
    connection = sqlite3.connect(db)
    connection.text_factory = str
    with connection:
        cursor = connection.cursor()
        cursor.execute("SELECT label, probability, url, freebase_id from labels as l JOIN urls as u on l.url_id = u.id where label=?", (name,))
        sresult = cursor.fetchall()
        print(sresult)
        # TODO: canonLabel? change dist?
        result_list = []
        for r in sresult:
            result = {
                'matched label': r[0],
                'db_id': r[2],
                'freebase_id': r[3],
                'prob': r[1]
            }
            result_list.append(result)
        return result_list

if __name__ == "__main__":
    db = sys.argv[1]
    app.run(port=5001, host='::', debug=False, use_reloader=False)
