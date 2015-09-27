#!/usr/bin/pypy
# Script for sqlite initialisation
# Init: ./sqlite-init.py labels.db dictionary.bz2

import sqlite3
import bz2
import sys


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


#the index takes another 6gb of memory, but lookup time decreases from 14s to 0.02s
def create_index(db):
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    cursor.execute("create INDEX index_label on labels(label)")
    connection.commit()


if __name__ == "__main__":
    db = sys.argv[1]
    dict_filename = sys.argv[2]
    init_database(db, dict_filename)
