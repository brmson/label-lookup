# label-lookup

Pseudo-fuzzy search script for dbpedia label lookup based on 
kitt.ai paper (http://aclweb.org/anthology/N/N15/N15-3014.pdf) by Xuchen Yao.

The script currently requires the labels_en.nq file to be in the same directory

Download it at  http://downloads.dbpedia.org/2015-04/core-i18n/en/labels_en.nq.bz2

Just run the script, wait about 2 minutes and then send requests to 
"localhost:5000/search/searchedlabel", for example "localhost:5000/search/AlbaniaPeople"
