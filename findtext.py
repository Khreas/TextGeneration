#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import sys
import os
from os import listdir, remove
from os.path import isfile, join

def getNameText(string):
	
	inputDirectory = 'gutenberg'

	file_list = [join(inputDirectory, f) for f in listdir(inputDirectory) if isfile(join(inputDirectory, f))]

	nb_file = 0
	cmd = 'subl '
	for file in file_list:
			with io.open(file, 'r', encoding='utf-8-sig') as input_file:
				for line in input_file:
					if string in line:
						print file
						os.system(cmd + file)
						nb_file+=1

	print "Number of file(s) found : %d" % nb_file

def findAllIncorrectTexts(inputDirectory):

	opening_chars = [u'(', u'[', u'{']
	closure_chars = [u')', u']', u'}']

	flag_chars = [0] * len(opening_chars)

	file_list = [join(inputDirectory, f) for f in listdir(inputDirectory) if isfile(join(inputDirectory, f))]

	incorrectTexts = []

	for file in file_list:
		with io.open(file, 'r', encoding='utf-8-sig', errors='ignore') as input_file:
			flag_chars = [0] * len(opening_chars)
			for line in input_file:
				for char in line:
					if char in opening_chars:
						flag_chars[opening_chars.index(char)] += 1
					elif char in closure_chars:
						flag_chars[closure_chars.index(char)] -= 1
		if flag_chars != [0] * len(opening_chars):
			incorrectTexts.append(file)

	return incorrectTexts

if __name__ == '__main__':
	
	getNameText(str(sys.argv[1]))