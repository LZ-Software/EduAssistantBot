import os
import string

from random import choice
from bs4 import BeautifulSoup

from downloader import Downloader


def get_rand_str(length):
	letters = string.ascii_lowercase
	rand_string = ''.join(choice(letters) for letter in range(length))
	return rand_string


def has_word(words, text):
	text = text.lower()
	for word in words:
		if word in text:
			return True
	return False


def get_name(link):
	i = str(link).rindex('/') + 1
	return link[i:]


class HTMLParser:

	__excluded_words = ('гиа', 'экз', 'зач', 'колледж', 'п.г', 'pdf', 'doc', 'docx')
	__file = None
	__files = dict()

	def get_html(self):
		self.__file = f'{get_rand_str(10)}.html'
		Downloader.download_file('https://www.mirea.ru/schedule/', self.__file)

	def delete_parsed_file(self):
		os.remove(self.__file)

	def parse_html(self):
		with open(self.__file, "r", encoding='utf-8') as file:
			contents = file.read()
			soup = BeautifulSoup(contents, 'lxml')
			files = soup.find_all('a', {'class': 'uk-link-toggle'})
			for s in files:
				s.find('div').replaceWith('')
				link = s['href']
				if not has_word(self.__excluded_words, link):
					name = get_name(link)
					self.__files[name] = link
		self.delete_parsed_file()

	def get_schedule_files(self):
		return self.__files
