import pickle
import logging
import requests
import pandas as pd
from bs4 import BeautifulSoup


BASE_URL = 'http://colleges.usnews.rankingsandreviews.com/best-colleges/rankings'
KEYS = ['score', 'school', 'location']


def scrape_link(url):
	'''
	Scrape a link and return HTML as a BeautifulSoup object
	'''
	response = requests.get(url)
	soup = BeautifulSoup(response.text, 'lxml')

	return soup


def parse_page(soup):
	'''
	Parse data from a page of scraped results into a pandas dataframe
	'''
	table = soup.find('table')

	scores = []
	schools = []
	locations = []

	for score in table.find_all('strong'):
		scores.append(score.findNextSibling().contents[0])

	for school in table.find_all(class_='school-name'):
		schools.append(school.contents[0])

	for location in table.find_all(class_='location'):
		locations.append(location.contents[0])

	# Append 'not ranked' to unranked colleges
	scores = scores + ['not ranked'] * (len(schools) - len(scores)) #Append "not ranked" to unranked colleges

	# return scraped dats as pandas dataframe
	data = dict(zip(['score', 'school', 'location'], [scores, schools, loctions]))

	return pd.DataFrame(data)


def get_max_page(soup):
	'''
	Determine the maximum number of pages for each category
	'''
	page_links = []

	for link in soup.find_all('a', href=True):
		if link['href'].find('page+') > 0:
			link = link['href'].encode("utf-8")
			page_num = ont(link[(link.find('+')+1):len(link)])

			page_links.append(page_num)

	return max(page_links)
	

def scrape_category(base_url, category):
	'''
	Scrape all pages for top 200 colleges in each category
	'''
	logger.info('Scraping: {category} Page: 1'.format(category))

	url = '{base}/{category}/data'.format(base=base_url, category=category)
	soup = scrape_link(url)

	df = parse_page(soup)
	max_page = get_max_page(soup)

	logger.info('{category} has {n} pages in total.'.format(category=category,
															n=max_page))

	
	for page in range(2, max_page + 1):
		logger.info('Scraping: {category}, Page: {page}'.format(category=category,
																page=page))


		url = '{base}/{category}/data/page+{page}'.format(base=base_url,
														  category=category,
														  page=page)

		soup = scrape_link(url)
		chunk = scrape_page(soup)
		

		df = pd.concat([df,page_df], axis=0, ignore_index=True)
		df['page'] = page

	df['category'] = category
	df.to_pickle('usnews-ranking-{url}.pickle'.format(url=cat_url))


if __name__ == '__main__':

	# Scrape Rankings from Each U.S News Category:
	# (1) National Universities
	# (2) National Liberal Arts Colleges
	# (3) Regional Universities (North, South, Midwest, West)
	# (4) Regional Colleges (North, South, Midwest, West)

	scrape_category(base_url=BASE_URL, cat_url='national-universities')
	scrape_category(base_url=BASE_URL, cat_url='national-liberal-arts-colleges')
	scrape_category(base_url=BASE_URL, cat_url='regional-universities-north')
	scrape_category(base_url=BASE_URL, cat_url='regional-universities-south')
	scrape_category(base_url=BASE_URL, cat_url='regional-universities-midwest')
	scrape_category(base_url=BASE_URL, cat_url='regional-universities-west')
	scrape_category(base_url=BASE_URL, cat_url='regional-colleges-north')
	scrape_category(base_url=BASE_URL, cat_url='regional-colleges-south')
	scrape_category(base_url=BASE_URL, cat_url='regional-colleges-midwest')
	scrape_category(base_url=BASE_URL, cat_url='regional-colleges-west')









