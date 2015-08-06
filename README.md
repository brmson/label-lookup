Fuzzy Label Lookup Service
==========================

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
(FIXME: Use DBpedia-2015-04 for the movies setting instead?)

First, we preprocess the dataset to build a single sorted list sorted_list.dat
to speed up next loadings:

	./preprocess.py labels_en.nt page-ids_en.nt sorted_list.dat

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

	./lookup-service.py

Wait about 5 minutes and then send requests to
``http://localhost:5000/search/<searchedlabel>``,
for example ``http://localhost:5000/search/AlbaniaPeople``.
It returns a json containing the label and it's wikipedia pageID.

Alternatively, it is possible to run it in interactive mode, but you have
to change the last line from ``web_init()`` to ``interactive()``.
