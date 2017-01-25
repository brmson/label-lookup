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

Freebase sqlite Lookup
-------------
This search script is based on 2 papers:
http://nlp.stanford.edu/pubs/crosswikis.pdf
http://ad-publications.informatik.uni-freiburg.de/CIKM_freebase_qa_BH_2015.pdf
Together with a list of freebase IDs.

It uses a sqlite database of search strings, wiki URLs and
the probability of the URL given the string. The dataset is located at

    http://nlp.stanford.edu/data/crosswikis-data.tar.bz2/

You will also need freebase_links_en.ttl, labels_en.tql, transitive_redirects_en.ttl from the
dbpedia dump page:

    http://wiki.dbpedia.org/downloads-2016-04

The database will be created automatically.
Fist, we need to preprocess the dataset to get a mapping from dbpedia ID to freebase ID

    python freebase_preprocess.py labels_en.tql transitive_redirects_en.ttl freebase_links_en.ttl sorted_fb_list.dat

To initialize the database, run 

    python freebase-init.py fb_db.sqlite dictionary sorted_fb_list.dat

It will initialize the database and create an index. The resulting size is roughly 9gb. Without the index, the size smaller, but a query takes 14s.

Then, start it like this:

	./lookup-service-fb.py fb_db.sqlite

It returns the matched label, the corresponding dbpedia id, a freebase id and
the probability of the dbpedia id giben the label.
To test it, send requests to ``http://localhost:5001/search/<searchedlabel>``
By default it searches the string in the database, it can also generate ngrams (by default to length
5) by appending ?ngrams=1 to the POST 
