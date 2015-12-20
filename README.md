Lookup Services
===============

Fuzzy lookup
------------

This is a pseudo-fuzzy search script for DBpedia label lookup inspired by the
kitt.ai paper (http://aclweb.org/anthology/N/N15/N15-3014.pdf) by Xuchen Yao.

Our motivation is to look up concepts and entities by their name even if it
contains typos or omissions.  This is designed as an external service to
conserve memory, allow even remote operation and pair up nicely with SPARQL
endpoints and such.

Setup
-----

Requirements: Couple of gigabytes of disk space for the dataset.
The preprocessing takes about 6GB of RAM; the service runtime stabilizes
on 4.5GB RAM usage.

### Data Preprocessing

Input data (DBpedia-2014):
  * http://downloads.dbpedia.org/2014/en/labels_en.nt.bz2
  * http://downloads.dbpedia.org/2014/en/page_ids_en.nt.bz2
  * http://downloads.dbpedia.org/2014/en/redirects_transitive_en.nt.bz2
(FIXME: Use DBpedia-2015-04 for the movies setting instead?)

First, we preprocess the dataset to build a single sorted list sorted_list.dat
to speed up next loadings:

	./preprocess.py labels_en.nt page_ids_en.nt redirects_transitive_en.nt sorted_list.dat

### Python Setup

Our Python executables use PyPy to speed things up (a lot).  Just install
it, or change the first line of the script to use Python instead).
However, you will also need to install the Flask module within PyPy
(already installed Python module won't do the trick).  Easiest is to
install PyPy-specific pip, then use it to install flask:

	curl -O https://bootstrap.pypa.io/get-pip.py
	pypy get-pip.py
	mv /usr/local/bin/pip ./pypy_pip
	./pypy_pip install flask

Usage
-----

Just run the script:

	./lookup-service.py sorted_list.txt

Wait until a confirmation message shows up and then send requests to
``http://localhost:5000/search/<searchedlabel>``,
for example ``http://localhost:5000/search/AlbaniaPeople``.
It returns a json containing the label, canon label and edit distance.

Alternatively, it is possible to run it in interactive mode, but you have
to change the last line from ``web_init()`` to ``interactive()``.

Sqlite Lookup
-------------
This search script is based on 2 papers:
http://nlp.stanford.edu/pubs/crosswikis.pdf
http://ad-publications.informatik.uni-freiburg.de/CIKM_freebase_qa_BH_2015.pdf

It uses a sqlite database of search strings, wiki URLs and
the probability of the URL given the string. The dataset is located at

	http://www-nlp.stanford.edu/pubs/crosswikis-data.tar.bz2/dictionary.bz2

The database will be created automatically.
To initialize the database, run 

	./sqlite-init.py labels.db dictionary.bz2

It will initialize the database and create an index. The resulting size is roughly 12GB. Without the index, the size is 6.6GB, but a query takes 14s.

Then, start it like this:

	./lookup-service-sqlite.py labels.db

It uses the same API as the fuzzy label lookup and should work the same.
To test it, send requests to ``http://localhost:5001/search/<searchedlabel>``

This API has an extra support for returning also the respective enwiki
pageId by querying DBpedia behind the scenes:
``http://localhost:5001/search/<searchedlabel>?addPageId=1``
