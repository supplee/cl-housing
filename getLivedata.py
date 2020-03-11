#!/usr/bin/python3

## getLiveData.py
## 		-get data for rent modeling from craigslist 
##		-store in a dataframe and save locally

# import get (similar to wget) to make and save an HTML request
# craigslist scraping tips courtesy of Riley Predum at Towards Data Science
from requests import get
from bs4 import BeautifulSoup
import sys
import re
import random
import h5py
import pandas as pd

myURL = "https://sfbay.craigslist.org/search/pen/apa?hasPic=1&availabilityMode=0&sale_date=all+dates"
debug = 1

# Apartment data structure
class Apartment:
	def __init__(self, sourceData, src='html'):
		self.rawData = sourceData
		self.src = src

		# Initialize with default values
		self.url = 'missing'
		self.pid = -1
		self.title = 'missing'
		self.date = ''
		self.price = -1
		self.hood = 'missing'
		self.rooms = -1
		self.bathrooms = 0
		self.area = -1
		self.attr = ''
		self.lat = ''
		self.lon = ''

		if debug:
			print("\nNEW APARTMENT CREATED")

		if self.src == 'html':
			# Craigslist post ID, URL, and title
			postID = sourceData.find('a',class_='result-title hdrlnk')
			self.url = postID['href']
			self.pid = int(postID['data-id'])
			self.title = postID.text.strip()
			self.title = self.title.replace('!',' ')
			self.title = self.title.strip()

			# Post date
			postDate = sourceData.find('time',class_='result-date')['datetime']
			postDate,postTime = postDate.split(' ')
			self.date = postDate
			#if debug:
			#	print("Posted on",self.date)

			# Price ('y' in our data set)
			postPrice = sourceData.find('span',class_='result-price')
			postPrice = postPrice.text.strip()
			postPrice = postPrice.strip('$')
			self.price = int(postPrice)
			if debug:
				print("On ",self.date,"(",self.pid,"): $",self.price,"-",self.title)

			# Neighborhood

			postHood = self.rawData.find('span', attrs={'class':'result-hood'})
			try:
				postHood = postHood.text
			except:
				postHood = 'missing'
			postHood = postHood.replace('(',' ')
			postHood = postHood.replace(')',' ')
			postHood = postHood.strip()
			self.hood = postHood.title()
			
			if debug:
				print("Located in",self.hood)

			# Bedrooms and size in square feet
			postRooms = sourceData.find('span',class_='housing')
			try:
				postRooms = postRooms.text.strip()
				postRooms = postRooms.strip('-')
				idx = postRooms.find("br")

				sizeIdx = postRooms.find("ft")
				#if debug:
				#	print(idx,sizeIdx,postRooms)
				if sizeIdx > 0:
					postSize = postRooms[idx+1:sizeIdx]
					postSize = postSize.replace('-',' ')
					postSize = postSize.replace('r',' ')
					postSize = postSize.strip()
					
					self.area = int(postSize)
				else:
					postSize = -1
					self.area = -1

				if idx > 0:
					postRooms = postRooms[0:idx]
				else:
					postRooms = 0	


			except:
				postRooms = "0"
				postSize = -1
			try:
				self.rooms = int(postRooms)
				if debug:
					print(self.rooms, "bedrooms")
					try:
						print(self.area,"sq ft")
					except:
						print("no area data found")
			except:
				self.rooms = 0
				self.area = -1


# Get craigslist housing posts and return as an array of HTML objects
def getPostData(baseURL=''):
	if baseURL == '':
		#baseURL = input('Enter a craigslist URL to get housing data from: ')
		baseURL = myURL

	# Get HTTP response from web server
	try:
		rawResponse = get(baseURL) # baseURL of first result page with relevant filters applied
		if debug > 1:
				print(rawResponse.text)
	except:
		print("Connection failed!")
		exit(1)

	# Parse results as HTML
	try:
		html_soup = BeautifulSoup(rawResponse.text, 'html.parser')
	except:
		print("Unable to interpret URL as HTML!")
		exit(2)

	# Get list of post objects
	posts = html_soup.find_all('li', class_='result-row')
	if debug:
		print(type(posts))
		print(len(posts))

	return posts

def getSavedListings(fileName='data.h5'):
	store = pd.HDFStore(fileName,'r')
	df = store['df']
	store.close()
	return df

# Takes data from the main table and scrapes additional attributes from each individual post page
def getMoreInformation(df):
	missingData = df.loc[df['attributes'] == '']
	for i in missingData['pid']:
		thisURL = missingData.loc[i,'url']
		try:
			rawResponse = get(thisURL)
		except:
			print("Unable to get HTTP request from",thisURL)
			exit(1)

		try:
			html_soup = BeautifulSoup(rawResponse.text, 'html.parser')
		except:
			print("Unable to parse request as HTML for record",p)
			exit(2)

		try:
			latData = html_soup.find('div',class_='viewposting')['data-latitude']
			lonData = html_soup.find('div',class_='viewposting')['data-longitude']
		except:
			latData = 0.00
			lonData = 0.00
		df.at[i,'latitude'] = latData
		df.at[i,'longitude'] = lonData

		# Fetch attributes and number of bathrooms, try again for area in sq ft if not found
		spans = html_soup.find_all('span',class_='shared-line-bubble')
		for span in spans:
			attrText = span.text
			try:
				idx = attrText.find("BR / ")
				if idx > 0:
					bathroomData = int(attrText[idx+5])
					df.at[i,'bathrooms'] = bathroomData

					if debug:
						print(bathroomData,"bathrooms")
			except:
				if debug:
					print("no bathroom data found")

			if df.at[i,'sqft'] < 0:
				attrText = attrText.strip()
				idx=attrText.find("ft2")
				if idx>0:
					areaData = attrText[0:idx]
					try:
						df.at[i,'sqft'] = int(areaData)
					except:
						df.at[i,'sqft'] = 0

		attributeString=''
		#pattrs=html_soup.find_all('p', class_='attrgroup')
		#for p in pattrs:
		#spans = p.findChildren('span',class_='', attr={'id': '', 'class': ''})
		spans = html_soup.find_all('span',class_='',attrs={'id':'', 'class':''})
		for span in spans:
			try:
				attr = span.text
				attr = attr.replace(' ','')
				if len(attr) > 8:
					attributeString += attr[:8]+"|"
				elif len(attr)>1 and len(attr) < 9:
					attributeString += attr+"|"
			except:
				next

#		attrData = html_soup.find_all('p', class_='attrgroup')
#		print(attrData)
#		attributeString = ''
#		bathroomData=0
#		for p in attrData:
#			attrText = p.span.text
#			print(attrText)
#
#			try:
#				idx = attrText.find("BR / ")
#				if idx > 0:
#					bathroomData = int(attrText[idx+5])
#					if debug:
#						print(bathroomData,"bathrooms")
#				elif attrText:
#					attrText = attrText.replace(' ','')
#					attrText = attrText.replace('\n','')
#					attrText = attrText.replace('\r','')
#					attrText = attrText[:8]
#					attributeString += attrText+'|'
#			except:
#				if debug:
#					print("no bathroom data found")
		print("Got apartment attributes:",attributeString)
		df.at[i,'attributes'] = attributeString
		try:
			df.at[i,'bathrooms'] = int(bathroomData)
		except:
			df.at[i,'bathrooms'] = 0
	if debug:
		print(missingData.tail())
	return df


def saveNewListings(apartments, fileName='data.h5',mode='overwrite'):
	if mode == 'overwrite':
		postsID = []
		postsDate = []
		postsURL = []
		postsTitle = []
		postsRooms = []
		postsBathrooms = []
		postsArea = []
		postsHood = []
		postsPrice = []
		postsAttr = []
		postsLat = []
		postsLon = []
	if mode == 'merge':
		store = pd.HDFStore(fileName,'r')
		dfSaved = store['df']
		postsID = dfSaved['pid'].tolist()
		postsDate = dfSaved['date'].tolist()
		postsHood = dfSaved['neighborhood'].tolist()
		postsTitle = dfSaved['title'].tolist()
		postsRooms = dfSaved['bedrooms'].tolist()
		postsBathrooms = dfSaved['bathrooms'].tolist()
		postsArea = dfSaved['sqft'].tolist()
		postsURL = dfSaved['url'].tolist()
		postsPrice = dfSaved['price'].tolist()
		postsAttr = dfSaved['attributes'].tolist()
		postsLat = dfSaved['latitude'].tolist()
		postsLon = dfSaved['longitude'].tolist()
		store.close()
		


	for a in apartments:
		# Create series from each scraped apartment listing
		postsID.append(a.pid)
		postsURL.append(a.url)
		postsDate.append(a.date)
		postsTitle.append(a.title)
		postsHood.append(a.hood)
		postsRooms.append(a.rooms)
		postsBathrooms.append(a.bathrooms)
		postsArea.append(a.area)
		postsPrice.append(a.price)
		postsAttr.append(a.attr)
		postsLat.append(a.lat)
		postsLon.append(a.lon)
	

	dfNew = pd.DataFrame({'pid': postsID,
		'date': postsDate,
		'neighborhood': postsHood,
		'title': postsTitle,
		'bedrooms': postsRooms,
		'bathrooms': postsBathrooms,
		'sqft': postsArea,
		'url': postsURL,
		'price': postsPrice,
		'attributes': postsAttr,
		'latitude': postsLat,
		'longitude': postsLon
		}, index=postsID)

	dfNew.drop_duplicates(inplace=True, keep='last')

	store = pd.HDFStore('data.h5','w')
	store['df'] = dfNew
	store.close()

	if debug:
		# If debugging, also save as csv for easy import and viewing
		[name,extension] = fileName.split('.')
		csvName = name+".csv"
		dfNew.to_csv(csvName)

	return dfNew

def main():
	try:
		posts=getPostData(sys.argv[1])
	except:
		posts=getPostData()

	# Turn each new post into a data object, to be converted to data frame
	apartments = []
	for p in posts:
		apartments.append(Apartment(p))
		if debug:
			print("\ncreated from SOURCE DATA:")
			print(p)

	# Save listings as data frame and to disk (in HDF5 format)
	# The 'merge' mode will merge the new posts with previously saved posts into one table
	saveNewListings(apartments, 'data.h5', mode='overwrite')
	topLevel=getSavedListings('data.h5')
	topLevel=getMoreInformation(topLevel)
	print(topLevel.tail())

	store = pd.HDFStore('data.h5','w')
	store['df'] = topLevel
	if debug:
		topLevel.to_csv('debug.csv')
	store.close()


	exit(0)

main()
