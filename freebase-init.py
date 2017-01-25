# !/usr/bin/pypy
# Script for sqlite initialisation
# Init: ./freebase-init.py labels.db dictionary.bz2 sorted_fb_list.dat
import sqlite3
import bz2
import sys

def init_database(db, dict_filename, fb_sorted_list):
    print('creating database')
    create_freebaseDB(db)
    print("populating database")
    populate_database(db, dict_filename, fb_sorted_list)
    print("creating index")
    create_index(db)
    print("done")

def create_freebaseDB(db_name):
    connection = sqlite3.connect(db_name)
    with connection:
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE urls
             (id integer PRIMARY KEY , url text, freebase_id text, UNIQUE(url))''')
        cursor.execute('''CREATE TABLE labels
             (id integer PRIMARY KEY , label text, probability real, url_id integer, FOREIGN KEY(url_id) REFERENCES urls(id))''')
        connection.commit()

def populate_database(db, dict_filename, fb_filename):
    connection = sqlite3.connect(db)
    fb_dict = {}
    with open(fb_filename) as fb:
        for line in fb:
            result = line.split('\t')
            label = result[0]
            db_url = result[1]
            fb_id = result[2]
            fb_dict[db_url] = fb_id
    input_file = open(dict_filename, 'rb')
    with connection:
        cursor = connection.cursor()
        connection.text_factory = str
        counter = 0
        not_found = 0
        for line in input_file:
            line = line.decode('latin-1')
            result = line.split('\t')
            label = result[0].lower()
            data = result[1].split(' ')
            probability = float(data[0])
            url = data[1]
            if url not in fb_dict:
                not_found += 1
                continue
            if not_found % 100000 == 0:
                print('not found:', not_found)
            if label != '' and probability > 0.05:
                if counter % 1000000 == 0:
                    print(str(counter))
                counter += 1
                cursor.execute('INSERT OR IGNORE INTO URLS(url, freebase_id) VALUES (?, ?)', (url, fb_id))
                cursor.execute('SELECT id from urls where url=?', (url,))
                urlid = cursor.fetchone()
                urlid = urlid[0]
                cursor.execute('INSERT INTO labels(label, probability, url_id) VALUES (?, ?, ?)', (label, probability, urlid))
        connection.commit()
        print("entres: ", counter)
        print('not found:', not_found)

def create_index(db):
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    cursor.execute("create INDEX index_label on labels(label)")
    connection.commit()

if __name__ == "__main__":
    db = sys.argv[1]
    dict_filename = sys.argv[2]
    fb_sorted_list = sys.argv[3]

    init_database(db, dict_filename, fb_sorted_list)
