#!/usr/bin/python3

## getLiveData.py
## 		get data for rent modeling from craigslist 
##

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
		self.area = -1

		if debug:
			print("\nNEW APARTMENT FOUND")
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
			postHood = sourceData.find('span',class_='result-hood')
			postHood = postHood.text
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

def saveNewListings(apartments, fileName='data.h5',mode='overwrite'):
	if mode == 'overwrite':
		postsID = []
		postsDate = []
		postsURL = []
		postsTitle = []
		postsRooms = []
		postsArea = []
		postsHood = []
		postsPrice = []

	for a in apartments:
		# Create vectors for a pandas dataframe
		print(a.area)

		postsID.append(a.pid)
		postsURL.append(a.url)
		postsDate.append(a.date)
		postsTitle.append(a.title)
		postsHood.append(a.hood)
		postsRooms.append(a.rooms)
		postsArea.append(a.area)
		postsPrice.append(a.price)
	

	dfNew = pd.DataFrame({'pid': postsID,
		'date': postsDate,
		'neighborhood': postsHood,
		'title': postsTitle,
		'bedrooms': postsRooms,
		'sqft': postsArea,
		'url': postsURL,
		'price': postsPrice
		}, index=postsID)

	store = pd.HDFStore('data.h5')
	store['df'] = dfNew

	if debug:
		# If debugging, also save as csv for easy import and viewing
		[name,extension] = fileName.split('.')
		csvName = fileName+".csv"
		dfNew.to_csv(csvName)


def main():
	try:
		posts=getPostData(sys.argv[1])
	except:
		posts=getPostData()

	# Turn each post into a data object, to be converted to data frame
	apartments = []
	for p in posts:
		apartments.append(Apartment(p))
		if debug:
			print("\ncreated from SOURCE DATA:")
			print(p)

	# Save listings as data frame (in HDF5 format)
	saveNewListings(apartments, 'data.h5', 'overwrite')

	exit(0)

main()
