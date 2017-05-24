#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import httplib2
import requests
import wget
import sys  
import logging
import re
import argparse
import zipfile
import os
import io
from os import listdir
from os.path import isfile, join, isdir
from bs4 import BeautifulSoup, SoupStrainer

if not os.path.exists('logs'):
    os.makedirs('logs')
logging.basicConfig(filename='logs/crawler.log',level=logging.DEBUG, format='%(asctime)s %(message)s',  datefmt='%d/%m/%Y %I:%M:%S %p')

def main():
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('--nb_files', type=int, default='100', help='Number of eBooks that will be downloaded by the script')
	parser.add_argument('--out_dir', type=str, default='./', help='Directory in which the texts will be stored (a subdir gutenberg_author / style will be created)')
	parser.add_argument('--crawl_type', type=str, default='authors', help='Indicate what the crawler should be looking for. Currently, "authors" and "styles" are available')
	args = parser.parse_args()

	crawler(args)
	compressFiles(args)

def crawler(args):

	if not os.path.exists(args.out_dir):
		os.makedirs(args.out_dir)

	website = "https://www.gutenberg.org"

	logging.debug("Beginning of the extraction")

	http = httplib2.Http()

	response = requests.get('https://www.gutenberg.org/wiki/Category:FR_Genre')

	logging.debug("Successfully loaded " + website)

	list_link = []
	list_book = []

	response = u'' + response.text
	# logging.debug("Website loaded in UTF-8 : " + str(isinstance(response, unicode)))

	if(args.crawl_type.lower() == 'authors'):

		for link in BeautifulSoup(response, "lxml", parse_only=SoupStrainer('a')).find_all('a'):

		        if str(link.get("href")).startswith("/"):
		        	list_link.append(website + link.get("href"))

		pattern = re.compile("^(//www.gutenberg.org/ebooks/)[0-9]+$")


		for link in list_link:
			response = requests.get(link)
			response = u'' + response.text
			for webpage in BeautifulSoup(response, "lxml", parse_only=SoupStrainer('a')).find_all('a'):
						if pattern.match(str(webpage.get('href'))):
							list_book.append(webpage.get('href'))


		for index, element in enumerate(list_book):
			list_book[index] = element[2:]


		nb_dl = 0

		for book in list_book:
			response = requests.get('http://' + book)
			response = u'' + response.text
			for webpage in BeautifulSoup(response.decode('utf-8'), "lxml", parse_only=SoupStrainer('a')).find_all('a'):
				if ".txt" in str(webpage.get('href')):
					wget.download('http:' + str(webpage.get('href')), out=os.path.join(args.out_dir, 'gutenberg_authors'))
					print("\neBook " + book + " successfully downloaded.\neBook (%d / %d)\n\n" %(nb_dl, args.nb_files))
					nb_dl = nb_dl + 1
				if nb_dl > args.nb_files:
					return

	elif args.crawl_type.lower() == 'styles':
		


		styles = ['Science_fiction', 'Théâtre', 'Nouvelles', 'Poésie', 'Séduction_et_libertinage']

		for link in BeautifulSoup(response, "lxml", parse_only=SoupStrainer('a')).find_all('a'):
			href_str = str(link.get("href"))
			if href_str.startswith("/"):
				for style in styles:
					if style in href_str:
						list_link.append((website + link.get("href"), style))

		pattern = re.compile("^(//www.gutenberg.org/ebooks/)[0-9]+$")

		for link in list_link:
			response = requests.get(link[0])
			response = u'' + response.text
			for webpage in BeautifulSoup(response.decode('utf-8'), "lxml", parse_only=SoupStrainer('a')).find_all('a'):
						if pattern.match(str(webpage.get('href'))):
							list_book.append((webpage.get('href'), link[1]))

		for index, element in enumerate(list_book):
			list_book[index][0] = (element[0][2:], element[1])

		nb_dl = 0

		for book in list_book:
			response = requests.get('http://' + book[0])
			response = u'' + response.text
			for webpage in BeautifulSoup(response.decode('utf-8'), "lxml", parse_only=SoupStrainer('a')).find_all('a'):
				if ".txt" in str(webpage.get('href')):
					wget.download('http:' + str(webpage.get('href')), out=os.path.join(args.out_dir, 'gutenberg_styles'))
					print("\neBook " + book[0] + " successfully downloaded. Style : %s\neBook (%d / %d)\n\n" %(book[1], nb_dl, args.nb_files))
					nb_dl = nb_dl + 1
				if nb_dl > args.nb_files:
					return

def compressFiles(args):
	mypath = args.out_dir
	if not os.path.isdir(mypath):
		print('No files available')
		sys.exit()
	with zipfile.ZipFile(args.out_dir.split('/')[-1] + ".zip", "w", zipfile.ZIP_DEFLATED) as fzip:
		for f in listdir(mypath):
			if isfile(join(mypath, f)):
				fzip.write(join(mypath, f))

if __name__ == '__main__':
	main()