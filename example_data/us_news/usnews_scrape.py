import requests
from bs4 import BeautifulSoup
import pandas as pd
import pickle


base_url="http://colleges.usnews.rankingsandreviews.com/best-colleges/rankings/"
keys=["score","school","location"]


#Scrape Scores, School Names and Locations from One Page of One Ranking of U.S. News Best Colleges
def scrape_page(soup, url):
	table=soup.find("table")

	scores=[]
	schools=[]
	locations=[]

	for score in table.find_all("strong"):
		scores.append(score.findNextSibling().contents[0])

	for school in table.find_all(class_="school-name"):
		schools.append(school.contents[0])

	for location in table.find_all(class_="location"):
		locations.append(location.contents[0])

	scores=scores+["not ranked"]*(len(schools)-len(scores)) #Append "not ranked" to unranked colleges

	df=pd.DataFrame(dict(zip(keys,[scores,schools,locations]))) #Compile Dataframe

	return df


#Determine the Maximum Number of Pages for Each Ranking Stratum
def scrape_max_page(soup, url):
	page_links=[]

	for link in soup.find_all("a", href=True):
		if link["href"].find("page+")>0:
			link=link["href"].encode("utf-8")
			page_num=int(link[(link.find("+")+1):len(link)])

			page_links.append(page_num)

	return max(page_links)
	

#Define a Function to Scrape all Scores, Names, and Locations for Top 200 Colleges
def scrape_category(cat_url):
	category=cat_url.replace("-"," ").title()

	url=base_url+cat_url+"/data"
	soup=BeautifulSoup(requests.session().get(url).text, "lxml")

	print "Scraping: "+category+" Page: 1"
	df=scrape_page(soup, url)
	max_page=scrape_max_page(soup, url)

	#print "Max Page is: "+str(max_page)

	for pg in range(2,(max_page+1)): #replace w/ total number of pages for each website
		print "Scraping: "+category+" Page: "+str(pg)

		url=base_url+cat_url+"/data/page+"+str(pg)
		soup=BeautifulSoup(requests.session().get(url).text, "lxml")
		page_df=scrape_page(soup, url)

		df=pd.concat([df,page_df], axis=0, ignore_index=True)
		df["category"]=category

	print df[["score","school"]].head(10)
	df.to_pickle("data/usnews-ranking-"+cat_url+".pickle")



#Scrape Rankings from Each U.S News Category:
#(1) National Universities
#(2) National Liberal Arts Colleges
#(3) Regional Universities (North, South, Midwest, West)
#(4) Regional Colleges (North, South, Midwest, West)

scrape_category("national-universities")
scrape_category("national-liberal-arts-colleges")

scrape_category("regional-universities-north")
scrape_category("regional-universities-south")
scrape_category("regional-universities-midwest")
scrape_category("regional-universities-west")

scrape_category("regional-colleges-north")
scrape_category("regional-colleges-south")
scrape_category("regional-colleges-midwest")
scrape_category("regional-colleges-west")









