#!/usr/bin/python
# Script for sqlite lookupfrom crossweb dataset
# Usage: ./lookup-service-sqlite.py labels.db

import sqlite3
import sys

from flask import *
app = Flask(__name__)

db = "fb_db.db"

def generate_ngrams(text, n=5):
    tokens = text.strip().split(' ')
    return (list(zip(*[tokens[i:] for i in range(k)])) for k in range(1,n+1))

@app.route('/search/<path:name>')  # Also supports ?ngrams=0
def web_search(name):
    # look for ngram or look just for the whole string
    ngrams = request.args.get('ngrams', False)
    result_list = []
    if ngrams:
        for ngram_list in generate_ngrams(name):
            for ngram in ngram_list:
                print('looking for:', ngram)
                result_list.append(search(" ".join(ngram)))
    else:
        print('looking for:', name)
        result_list.append(search(name))
    print(result_list)
    return jsonify(results=result_list[:3])


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
