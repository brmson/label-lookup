# label-lookup

Pseudo-fuzzy search script for dbpedia label lookup based on 
kitt.ai paper (http://aclweb.org/anthology/N/N15/N15-3014.pdf) by Xuchen Yao.

The script currently requires the labels_en.nq and page-ids-en.nq files to be in the same directory

Download it at  http://downloads.dbpedia.org/2015-04/core-i18n/en/labels_en.nq.bz2
				http://downloads.dbpedia.org/2015-04/core-i18n/en/page-ids_en.nq.bz2

After sorting and merging both lists, it creates a file called sorted_list.dat, which is used
to speed up loading

Just run the script, wait about 5 minutes and then send requests to 
"localhost:5000/search/searchedlabel"
for example "localhost:5000/search/AlbaniaPeople"
Alternatively, it is possible to run it in interactive mode, but you have
to change "if __name__ == "__main__": web_init()" to 
"if __name__ == "__main__": interactive()"

It returns a json containing the label and it's wikipedia pageID.
