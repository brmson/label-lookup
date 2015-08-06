Fuzzy Label Lookup Service
==========================

This is a pseudo-fuzzy search script for DBpedia label lookup inspired by the
kitt.ai paper (http://aclweb.org/anthology/N/N15/N15-3014.pdf) by Xuchen Yao.

Our motivation is to look up concepts and entities by their name even if it
contains typos or omissions.  This is designed as an external service to
conserve memory, allow even remote operation and pair up nicely with SPARQL
endpoints and such.

Initialization
--------------

Input data:
  * http://downloads.dbpedia.org/2015-04/core-i18n/en/labels_en.nq.bz2
  * http://downloads.dbpedia.org/2015-04/core-i18n/en/page-ids_en.nq.bz2

(FIXME: We may want to use DBpedia-2014 consistent with our YodaQA scientific
setting instead?)

The script currently requires the labels_en.nq and page-ids-en.nq files to be in the same directory.
After sorting and merging both lists, it creates a file called sorted_list.dat, which is used
to speed up loading.

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
