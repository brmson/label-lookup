#!/usr/bin/pypy
# Script for sqlite lookupfrom crossweb dataset
# Init: ./lookup-service-sqlite.py labels.db dictionary.bz2
# Usage: ./lookup-service-sqlite.py labels.db

import sqlite3
import bz2
import sys
from flask import *
app = Flask(__name__)
db = "labels.db"


def init_database(db, dict_filename):
    print("populating database")
    populate_database(db, dict_filename)
    print("creating index")
    create_index(db)
    print("done")


def populate_database(db, dict_filename):
    connection = sqlite3.connect(db)
    input_file = bz2.BZ2File(dict_filename, 'r')
    with connection:
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE urls
             (id integer PRIMARY KEY , url text, UNIQUE(url))''')
        cursor.execute('''CREATE TABLE labels
             (id integer PRIMARY KEY , label text, probability real, url_id integer, FOREIGN KEY(url_id) REFERENCES urls(id))''')
        connection.text_factory = str
        counter = 0
        for line in input_file:
            result = line.split('\t')
            label = result[0]
            data = result[1].split(' ')
            probability = float(data[0])
            url = data[1]
            if label != '' and probability > 0.05:
                if counter % 1000000 == 0:
                    print str(counter)
                counter += 11
                cursor.execute('INSERT OR IGNORE INTO URLS(url) VALUES (?)', (url,))
                cursor.execute('SELECT id from urls where url=?', (url,))
                urlid = cursor.fetchone()
                urlid = urlid[0]
                cursor.execute('INSERT INTO labels(label, probability, url_id) VALUES (?, ?, ?)', (label, probability, urlid))
        connection.commit()
        connection.close()

#the index takes another 6gb of memory, but lookup time decreases from 14s to 0.02s
def create_index(db):
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    cursor.execute("create INDEX index_label on labels(label)")
    connection.commit()


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
    #dict_filename = sys.argv[2]
    #init_database(db, dict_filename)
    app.run(port=5001, host='0.0.0.0', debug=False, use_reloader=False)
