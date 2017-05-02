#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import io
import time
import logging
import re
import zipfile
import sys

from os import listdir, remove
from os.path import isfile, join, isdir
from findtext import findAllIncorrectTexts

logging.basicConfig(filename='logs/inputGeneration.log',level=logging.DEBUG, format='%(asctime)s %(message)s',  datefmt='%d/%m/%Y %I:%M:%S %p')

def concatenateFiles(inputDirectory, outputFile, args):
	
	logging.info("Concatenation : started")

	if not isdir('gutenberg'):
		if isfile('gutenberg.zip'):
			print 'Extracting files ...'
			zipfile.ZipFile("gutenberg.zip", "r").extractall()
		else:
			print 'No files available. Program will now exit.'
			sys.exit()

	file_list = [join(inputDirectory, f) for f in listdir(inputDirectory) if isfile(join(inputDirectory, f))]

	logging.info("	Finding incorrect Texts : started")
	rejected_files = findAllIncorrectTexts(inputDirectory)
	logging.debug("	Number of incorrect texts found: %d" % len(rejected_files))
	logging.info("	Finding incorrect Texts : done in %3f seconds" % (time.time() - start))

	nb_files = 0

	with io.open(outputFile, 'w', encoding='utf-8-sig') as output_file:
		for file in file_list:
			if nb_files > args.nb_files:
				break
			if file not in (filepath for filepath in rejected_files):
				with io.open(file, 'r', encoding='utf-8-sig', errors='ignore') as input_file:
					output_file.write(input_file.read())
					nb_files += 1

	logging.info("Last file processed : " + file_list[-1])
	logging.info("Number of files loaded : %d" %nb_files)
	logging.info("Concatenation : done in %s" %(time.time() - start))

def cleanText(inputFile, outputFile, args):

	logging.info("Cleaning : started at %s" % (time.time() - start))
	print 'Cleaning started'
	last_char = ''

	opening_header = [u'Project Gutenberg', u'Project gutenberg', u'project gutenberg']
	opening_footer = [u'END OF', u'End of']

	closure_header = [u'START OF', u'Start of']
	closure_footer = [u'subscribe']

	useless_chars = [u'_']

	useless_pattern = [re.compile("<.+>"), re.compile("</.+>")]

	skip_patterns = [u'=>', u'<=', u'       ']

	opening_chars = [u'(', u'[', u'{']
	closure_chars = [u')', u']', u'}']
	flags_chars = [0, 0, 0]
	dont_write_char = 0
	dont_write_line = 0
	skip_line = 1


	with io.open(inputFile, 'r', encoding='utf-8-sig', errors='ignore') as input_file, io.open(outputFile, 'w', encoding='utf-8-sig') as output_file:
		for line in input_file:

			if any(op_h in line for op_h in opening_header) or any(op_f in line for op_f in opening_footer):
				dont_write_line = 1

			elif re.compile("Produced").match(line):
				skip_line += 5

			elif line.isupper() and not (any(op_c in line for op_c in opening_chars) or any(cl_c in line for cl_c in closure_chars)):
				skip_line += 1

			elif not line.strip():
				skip_line += 1

			else:
				for pattern in skip_patterns:
					if pattern in line and not any(op_c in line for op_c in opening_chars) and not any(cl_c in line for cl_c in closure_chars):
						skip_line += 1
						break

				for pattern in useless_pattern:
					if pattern.search(line):
						line = re.sub(pattern, "", line)
			

			if dont_write_line == 0 and skip_line == 0:
				for char in line:
					if not char in useless_chars:
						
						if char in opening_chars:
							flags_chars[opening_chars.index(char)] += 1

						if last_char == u'>':
							if char == u'>':
								char = u' »'
							elif not any(flag > 0 for flag in flags_chars):
								output_file.write(u">")

						elif char == u'>':
							dont_write_char = 1

						if last_char == u'<':
							if char == u'<':
								char = u'« '
							elif not any(flag > 0 for flag in flags_chars):
								output_file.write(u"<")

						elif char == u'<':
							dont_write_char = 1

						if last_char == u'-':
							if char == u'-':
								char = u'— '
							elif not any(flag > 0 for flag in flags_chars):
								output_file.write(u"-")

						elif char == u'-':
							dont_write_char = 1

						if all(flag == 0 for flag in flags_chars) and dont_write_char == 0:
							output_file.write(char)

						elif char in closure_chars:
							flags_chars[closure_chars.index(char)] -= 1

						dont_write_char = 0
						last_char = char

			elif any(cl_h in line for cl_h in closure_header) or any(cl_f in line for cl_f in closure_footer):
				dont_write_line = 0
			
			if skip_line > 0:
				skip_line -= 1

	end_clean = time.time()
	logging.info("Cleaning : done at %s" %(end_clean - start))
	
	logging.info("Zipping started")

	with zipfile.ZipFile(outputFile[:-4] + ".zip", "w", zipfile.ZIP_DEFLATED) as fzip:
		fzip.write(outputFile, arcname='input.txt')

	logging.info("Zipping ended. Took %3f" %(time.time() - end_clean))

if __name__ == '__main__':

	parser = argparse.ArgumentParser(
                       formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('--nb_files', type=int, default=100,
						help='number of files to deal with')

	args = parser.parse_args()

	inpath = 'gutenberg'
	outpath = 'data/french/input.txt'
	tmpath = 'data/french/input_tmp.txt'

	start = time.time()

	concatenateFiles(inpath, tmpath, args)
	cleanText(tmpath, outpath, args)
	remove("data/french/input_tmp.txt")

	logging.info("Program ran in %s seconds" % (time.time() - start))