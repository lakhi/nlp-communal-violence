import nltk
from nltk import word_tokenize
import os
from os.path import isfile, join
import re

path = './workspace/preassignment/'
actors = ['Hind', 'Musl', 'Sikh', 'Jew', 'Christian', 'Parsi'] 		# List of potential actors: https://en.wikipedia.org/wiki/Religious_violence_in_India

"""
	Each txt file becomes a Page object for us, with the following attributes:
	fname, header, artilces[], article_titles[], CondFreqDist cfd, cviolence_article_title and an object of the CommunalViolence class
"""	
class Page:	
	def __init__(self, fname):
		self.fname = fname
		raw = open(path + fname, encoding='utf8').read()
		raw = raw[:raw.rfind('Reproduced with permission of the copyright owner.')] 	#  Remove the copyright line
		
		self.header = raw[:re.search('(p|P)g', raw).start()]		# Header consists of data from the start of the text until it gets the page number('pg')
		
		self.articles = []
		# Regex expression which pattern matches for the start of a new article. The pattern being: "MADRAS, October 5"
		self.article_titles = re.findall(r'[A-Z]+, (?:September|October) [0-9]{1,2}', raw)
			
		for last_article in reversed(self.article_titles):			# Start from the last article in the article_titles
			self.articles.append(raw[raw.rfind(last_article):])		# Keep appending each article from the end of the text to the list of articles[]
			raw = raw[:raw.rfind(last_article)]  	
		
		if not self.article_titles:									# "MADRAS, October 5" type of pattern did not match implies that page is of form text 3.txt
			index_of_header_end = raw.find('\n', len(self.header))	# Hence make the title of the article the line following the header
			self.articles.append(raw[index_of_header_end + 1:])
			self.article_titles.append(raw[index_of_header_end + 1 : raw.find('\n', index_of_header_end + 1)])
		
		self.cfd = []
		self.cviolence_article_title = ''
		cviolence_article = self.get_cviolence_article()
		
		# Initialize our CommunalViolence object from the article on communal violence that we extract from the list of articles in the page
		self.cviolence = CommunalViolence(self.cviolence_article_title, cviolence_article)	
		
	def __str__(self):
		print("********************************< PAGE OBJECT >********************************\n\n")
		print("File Name: " + self.fname + "\n")
		print("++++++++++++ Header: \n" + self.header + "\n++++++++++++\n")
		print("---------------- ARTICLES ----------------\n")
		for title in self.article_titles:
			print("____________ Article Title: " + title + "____________\n")
		for article in self.articles:
			print("++++++++++++ Article: \n" + article + "\n++++++++++++\n")
		print("------------- END OF ARTICLES ------------\n")	
		print("\n\n********************************</ PAGE OBJECT />******************************")
		return ''
		
	"""
		Out of the several articles in the page, we are interested in the communal violence one.
		This method computes a CondFreqDist for the number of times an actor (Hind/Musl) is mentioned in an article
		We then sum up the total mentions of each actor in the title_sum_list
		The title in which the sum_of_actor mentions is the maximum is the article on communal violence that we are interested in.
	"""
	def get_cviolence_article(self):
		self.cfd = nltk.ConditionalFreqDist((article_title, actor)
								for article_title in self.article_titles
								for actor in actors
								for article in self.articles
								for token in word_tokenize(article)
								if article.startswith(article_title) and actor in token)
	#	self.cfd.tabulate()			
		
		title_sum_list = []
		for title in self.article_titles:
			sum_of_actors = 0
			for actor in actors:
				sum_of_actors += self.cfd[title][actor]
			title_sum_list.append((sum_of_actors, title))
		title_sum_list.sort()
		
		self.cviolence_article_title = str(title_sum_list.pop()[1])
		for article in self.articles:
			if article.startswith(self.cviolence_article_title):
				cviolence_article = article
				
		return cviolence_article
	
	"""
		Navigates the cfd to check which actors are involved in the communal violence artice.
	"""
	def get_cviolence_actors(self):
		cviolence_actors = []
		for actor in actors:
			if self.cfd[self.cviolence_article_title][actor] > 0:
				cviolence_actors.append(actor)
				
		return str(cviolence_actors)
		
	def get_name(self):
		return self.fname
		
	""" 
		The following member functions are handled in this way for data encapsulation, 
		a fundamental principle of object-oriented programming
	"""
	def get_cviolence_date(self):
		return self.cviolence.get_date()
		
	def get_cviolence_place(self):
		return self.cviolence.get_place()

	def get_cviolence_deaths(self):
		return self.cviolence.get_deaths()

	def get_cviolence_injured(self):
		return self.cviolence.get_injured()

	def get_cviolence_arrests(self):
		return self.cviolence.get_arrests()	
		
class CommunalViolence:
	def __init__(self, cviolence_title, cviolence_article):
		self.cviolence_title = cviolence_title
		self.cviolence_article = cviolence_article
		self.date = []
		self.place = []
		self.injured = []
		self.arrests = []
		self.deaths = []
		self.cviolence_tokenized = word_tokenize(self.cviolence_article)

	""" 
		Pattern: October 5 | September 26 | January 8
		Approach: First priority search in article, if not found then search in article title
		for relative search regex of predetermined words like yesterday, last evening, etc.
	"""
	def	get_date(self):
		absolute_date_regexp = r'(?:January|September|October) [0-9]{1,2}[^ 0-9]'
		relative_date_regexp = r'(yesterday|day before|last night|last evening)'
		
		self.date = re.findall(absolute_date_regexp, self.cviolence_article[len(self.cviolence_title)+1 : ])
		if not self.date:
			self.date = re.findall(absolute_date_regexp, self.cviolence_article[:len(self.cviolence_title)+1])
		
		relative_date = re.findall(relative_date_regexp, self.cviolence_article)
		if relative_date:
			self.date.append(relative_date[0])
		return str(self.date)
		
	def get_place(self):
		place_regexp = r'(?:in the|of|at) [A-Z]+[a-z]* [, a-z]*'
		self.place = re.findall(place_regexp, self.cviolence_article)
		
		if(self.cviolence_tokenized[0].isupper()):
			self.place.append(self.cviolence_tokenized[0])
		return str(self.place)
		
	""" 
		Pattern: '...........were .... injured ..'
	"""
	def get_injured(self):
		injured_regexp = r'<.*>{10} <were> <.*?> <injured>'	
		self.injured = re.findall(injured_regexp, self.cviolence_article)
		return str(self.injured)
		
	def get_deaths(self):
		deaths_regexp = r'[ \w]{11} were killed'
		self.deaths = re.findall(deaths_regexp, self.cviolence_article)
		return str(self.deaths)
		
	def get_arrests(self):
		arrests_regexp = r'[: \w]{29} were arrested'
		self.arrests = re.findall(arrests_regexp, self.cviolence_article)
		return str(self.arrests)	
	
def list_files(path): 			# returns a list of names of all the txt files in the directory: '19301006_751257422_5978.txt'
	return [f for f in os.listdir(path) if isfile(join(path, f)) and f[-3:] == 'txt']	

files = list_files(path)
for file in files:
	page = Page(file)
	print('# ' + page.get_name() + '\n')
	print("* Date: " + page.get_cviolence_date())
	print("* Place: " + page.get_cviolence_place())
	print("* Actors: " + str(page.get_cviolence_actors()))
	print("* Deaths: " + page.get_cviolence_deaths())
	print("* Injured: " + str(page.get_cviolence_injured()))
	print("* Arrests: " + page.get_cviolence_arrests() + "\n\n")
		