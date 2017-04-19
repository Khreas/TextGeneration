#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import time
import logging
import re

from os import listdir, remove
from os.path import isfile, join
from findtext import findAllIncorrectTexts

logging.basicConfig(filename='logs/cleanText.log',level=logging.DEBUG)

def concatenateFiles(inputDirectory, outputFile):
	
	logging.info("Concatenation : started")

	file_list = [join(inputDirectory, f) for f in listdir(inputDirectory) if isfile(join(inputDirectory, f))]

	logging.info("	Finding incorrect Texts : started")
	rejected_files = findAllIncorrectTexts(inputDirectory)
	logging.debug("	Number of incorrect texts found: %d" % len(rejected_files))
	logging.info("	Finding incorrect Texts : done in %3f seconds" % (time.time() - start))

	with io.open(outputFile, 'w', encoding='utf-8-sig') as output_file:
		for file in file_list:
			if file not in (filepath for filepath in rejected_files):
				with io.open(file, 'r', encoding='utf-8-sig', errors='ignore') as input_file:
					output_file.write(input_file.read())

	logging.info("Last file processed : " + file_list[-1])

	logging.info("Concatenation : done in %s" %(time.time() - start))

def cleanText(inputFile, outputFile):

	logging.info("Cleaning : started at %s" % (time.time() - start))

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


	logging.info("Cleaning : done at %s" %(time.time() - start))

if __name__ == '__main__':

	inpath = 'gutenberg'
	outpath = 'data/french/input.txt'
	tmpath = 'data/french/input_tmp.txt'

	start = time.time()

	concatenateFiles(inpath, tmpath)
	cleanText(tmpath, outpath)
	remove("data/french/input_tmp.txt")

	logging.info("Program ran in %s seconds" % (time.time() - start))