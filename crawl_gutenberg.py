import httplib2
import wget
import sys  
import logging
import re
import argparse
from bs4 import BeautifulSoup, SoupStrainer

reload(sys)
sys.setdefaultencoding('utf8')

def main():
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('--nb_files', type=int, default='100', help='Number of eBooks that will be downloaded by the script')
	parser.add_argument('--out_dir', type=str, default='gutenberg', help='Directory in which the texts will be stored')

	args = parser.parse_args()

	crawler(args)

def crawler(args):

	website = "https://www.gutenberg.org"

	logging.debug("Beginning of the project")

	http = httplib2.Http()
	status, response = http.request('https://www.gutenberg.org/wiki/Category:FR_Genre')

	logging.debug("Successfully loaded " + website)

	list_link = []
	list_book = []

	response = u'' + response
	logging.debug("Website loaded in UTF-8 : " + str(isinstance(response, unicode)))

	for link in BeautifulSoup(response, "lxml", parse_only=SoupStrainer('a')).find_all('a'):

	        if str(link.get("href")).startswith("/"):
	        	list_link.append(website + link.get("href"))

	pattern = re.compile("^(//www.gutenberg.org/ebooks/)[0-9]+$")

	for link in list_link:
		status, response = http.request(link)
		response = u'' + response
		for webpage in BeautifulSoup(response.decode('utf-8'), "lxml", parse_only=SoupStrainer('a')).find_all('a'):
					if pattern.match(str(webpage.get('href'))):
						list_book.append(webpage.get('href'))

	for index, element in enumerate(list_book):
		list_book[index] = element[2:]

	nb_dl = 0

	for book in list_book:
		status, response = http.request('http://' + book)
		response = u'' + response
		for webpage in BeautifulSoup(response.decode('utf-8'), "lxml", parse_only=SoupStrainer('a')).find_all('a'):
			if ".txt" in str(webpage.get('href')):
				wget.download('http:' + str(webpage.get('href')), out=args.out_dir)
				print "\neBook " + book + " successfully downloaded.\neBook (%d / %d)\n\n" %(nb_dl, args.nb_dl)
				nb_dl = nb_dl + 1
			if nb_dl > args.nb_files:
				return

if __name__ == '__main__':
	main()