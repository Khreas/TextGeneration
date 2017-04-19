#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io


def cleanCharacters():
	last_char = ''

	flag = 0
	dont_write_char = 0

	with io.open('input.txt', 'r', encoding='utf-8') as input_file, io.open('output.txt', 'w', encoding='utf-8') as output_file:
		for line in input_file:
			for char in line:
				if char == u'[':
					flag = 1

				if last_char == u'>':
					if char == u'>':
						char = u' »'
					else:
						char = u'>' + char

				elif char == u'>':
					dont_write_char = 1

				if last_char == u'<':
					if char == u'<':
						char = u'« '
					else:
						char = u'<' + char

				elif char == u'<':
					dont_write_char = 1

				if last_char == u'-':
					if char == u'-':
						char = u'— '
					else:
						char = u'-' + char

				elif char == u'-':
					dont_write_char = 1

				if flag != 1 and char != u'_' and dont_write_char == 0:
					output_file.write(char)
					
				if char == ']':
					flag = 0

				dont_write_char = 0
				last_char = char