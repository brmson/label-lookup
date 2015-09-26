#!/usr/bin/pypy
# Script for sqlite lookupfrom crossweb dataset
# Usage: ./lookup-service-sqlite.py labels.db

import sqlite3
import sys
from flask import *
app = Flask(__name__)
db = "labels.db"


@app.route('/search/<path:name>')
def web_search(name):
    print "searching " + name
    global dataset
    result_list = search(name)
    print "found:"
    print result_list[:3]
    return jsonify(results=result_list[:3])


def search(name):
    connection = sqlite3.connect(db)
    connection.text_factory = str
    with connection:
        cursor = connection.cursor()
        cursor.execute("SELECT label, probability, url from labels as l JOIN urls as u on l.url_id = u.id where label=?", (name,))
        result = cursor.fetchall()
        #TODO: canonLabel? change dist?
        result_list = [{
            'matchedLabel': r[0],
            'canonLabel': r[2],
            'name': r[2],
            'dist': 0,
            'prob': r[1]
        } for r in result]
        return result_list


if __name__ == "__main__":
    db = sys.argv[1]
    app.run(port=5001, host='0.0.0.0', debug=False, use_reloader=False)
