#!/usr/bin/python3

import getLivedata as gl
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import os
import re

#fileName = 'data.h5'
#outputFile = 'cleandata.h5'
debugVis = 1

#df = gl.getDataFromDisk(fileName)
#os.system("cp "+fileName+" "+fileName+".bak")
#df = pd.read_csv("debug.csv")
#if debugVis:
#	df.to_csv('debug.csv')

#df = gl.getMissingInformation(df,limit=120)

#df2 = gl.purgeMissingData(df)


#
#pd.set_option('display.max_rows', 60)
#pd.set_option('display.max_columns', None)
#pd.set_option('display.max_colwidth', 32)

#tf = df.copy()
#print(tf.neighborhood.describe())
#print(tf.neighborhood.value_counts())

def PetsOK(row):
	if bool(re.match(u'.*catsare.*',row.attributes)) or bool(re.match(u'.*dogsare.*',row.attributes)):
		return True
	else:
		return False

def hasLaundry(row):
	try:
		if bool(re.match(u'.*w/d.*',row.attributes)) or bool(re.match(u'.*laundryi.*',row.attributes)):
			return 2
		elif bool(re.match(u'.*laundryo.*',row.attributes)):
			return 1
		else:
			return 0
	except:
		return False

def hasParking(row):
	counter=0
	try:
		if bool(re.match(u'.*carport.*',row.attributes)):
			counter+=2
		if bool(re.match(u'.*garage.*',row.attributes)):
			counter+=2
		if bool(re.match(u'.*attached.*',row.attributes)):
			counter+=2
		if bool(re.match(u'.*detached.*',row.attributes)):
			counter+=2
		if bool(re.match(u'.*off-stre.*',row.attributes)):
			counter+=1
		if bool(re.match(u'.*streetpa.*',row.attributes)):
			counter=0
		return counter
	except:
		return np.nan

def hasEVcharging(row):
	if bool(re.match(u'.*evchargi.*',row.attributes)):
		return True
	else:
		return False

def generateHeatmap(df,dimensions=[':']):
	temp = df.loc[:,dimensions]
	corr = temp.corr()
	return sns.heatmap(corr,xticklabels=corr.columns,yticklabels=corr.columns)

def densityByNeighborhood(df,colName='price'):
	names = df.neighborhood.unique()

	for name in names:
		subset = df[df['neighborhood'] == name]

		# Draw the density plot
		sns.distplot(subset[colName], hist=False, kde=True,
			kde_kws={'linewidth': 2},
			label=name)

	plt.legend(prop={'size':16}, title='Neighborhood')
	plt.title('Density of'+colName+'for each neighborhood')
	plt.ylabel('Density')
	plt.show()

#tf['post_per_neighborhood'] = tf['neighborhood'].aggregate(np.count_nonzero)
#print(tf.tail())

# CLEAN UP OUTLIERS
#Drop records belonging to a neighborhood with fewer than 5 posts
#byNeighborhood = tf.groupby('neighborhood')
#junk = byNeighborhood.filter(lambda x : len(x)<3).index
#print(tf.loc[junk])
#tf=tf.drop(junk)

# Drop records with no bathrooms
#junk=tf[tf['bathrooms']==0].index
#tf=tf.drop(junk)

# Look for duplicate posts (same title + number of bedrooms)
#print("Finding duplicates...\n")
#junk=tf.loc[:,['pid','title','bedrooms']]
#junk.sort_values(['pid'],ascending=True,inplace=True,axis=0)
#print(junk[junk[['title','bedrooms']].duplicated(keep=False) == True].describe())
#duplicates=tf.loc[junk[['title','bedrooms']].duplicated(keep='last') == True]
#tf = tf.drop(duplicates.index)

# LET'S VISUALIZE!
#ax=sns.regplot(x='bedrooms',y='price',data=tf)
#ax.set_title('Monthly rent depends on number of bedrooms')
#ax.set_ylabel('dollars per month')
#plt.show()

#sns.set_style("ticks")
#ax=sns.barplot(x='bedrooms',y='price',data=tf)
#ax.set_ylabel('$ per month')
#ax.set_title('Average rent depends on the number of bedrooms')
#plt.show()
def placeholder():
	areaData = tf[tf['sqft']>0]
	areaTable = areaData.loc[:, ['neighborhood','bedrooms','bathrooms','sqft','attributes','price']]
	areaTable['$/sqft'] = areaData.apply(lambda x : x.price/x.sqft,axis=1)
	areaTable['pets?'] = areaData.apply(lambda x : PetsOK(x),axis=1)
	
#ax = sns.boxplot(x='neighborhood', y='$/sqft', data=areaTable, orient="v")
#plt.show()
def placeholer2():
	ax = sns.boxplot(x='pets?', y='$/sqft', data=areaTable, orient="v")
	plt.show()

	ax = sns.distplot(tf.price)
	plt.show()

#fig,ax=plt.subplots()
#ax=sns.distplot(areaTable.sqft)
#ax.set_xlim(0,1000)
#ax.set_xticks(range(0,1000,100))
#plt.show()

# Check univariate distribution by normalizing data
#	bathrooms
#	bedrooms
#	price
#	lat
#	long
def univariate():
	univariateSlice = tf.copy()
	bedroomMean = univariateSlice['bedrooms'].mean()
	bedroomStd = univariateSlice['bedrooms'].std()
	bathroomMean = univariateSlice['bathrooms'].mean()
	bathroomStd = univariateSlice['bathrooms'].std()
	priceMean = univariateSlice['price'].mean()
	priceStd = univariateSlice['price'].std()
#latMean = univariateSlice['latitude'].mean()
#latStd = univariateSlice['latitude'].std()
#lonMean = univariateSlice['longitude'].mean()
#lonStd = univariateSlice['longitude'].std()

	univariateSlice['normalized_bedrooms'] = univariateSlice.apply(lambda x : (x.bedrooms-bedroomMean)/bedroomStd,axis=1)
	univariateSlice['normalized_bathrooms'] = univariateSlice.apply(lambda x : (x.bathrooms-bathroomMean)/bathroomStd,axis=1)
	univariateSlice['normalized_price'] = univariateSlice.apply(lambda x : (x.price-priceMean)/priceStd,axis=1)
	ppsqftMean = areaTable['$/sqft'].mean()
	ppsqftStd = areaTable['$/sqft'].std()
	areaTable['normalized_ppsqft'] = areaTable.apply(lambda x : (x['$/sqft']-ppsqftMean)/ppsqftStd,axis=1)
#univariateSlice['normalized_latitude'] = univariateSlice.apply(lambda x : (x.latitude-latMean)/latStd,axis=1)
#univariateSlice['normalized_longitude'] = univariateSlice.apply(lambda x : (x.longitude-lonMean)/lonStd,axis=1)

	univariateView = univariateSlice.loc[:,['pid','normalized_bedrooms','normalized_bathrooms','normalized_price']]
#ax = sns.boxplot(x=['normalized_bedrooms'],data=univariateSlice,orient='v')
#ax2 = plt.subplots()
#ax2 = sns.boxplot(x=['normalized_bathrooms'],data=univariateSlice,orient='v')
#ax.set_xlabel('bedrooms')
#ax.set_ylabel('z-score')
#ax.set_title('univariate distribution for number of bedrooms')
#ax2.set_xlabel('bathrooms')
#ax2.set_ylabel('z-score')
#ax2.set_title('univariate distribution for number of bathrooms')
#ax3=plt.subplots()
#ax3=sns.boxplot(x='normalized_ppsqft',data=areaTable,orient='v')
#ax3.set_title('univariate distribution for $/sqft')
#ax3.set_xlabel('$/sqft')
#ax3.set_ylabel('z-score')
#plt.show() 

#g=sns.catplot(x="neighborhood",y="$/sqft",kind="box",data=areaTable)
#plt.show()
#g = sns.FacetGrid(areaTable, col="neighborhood", col_wrap=4, ylim=(0,8))
#g.map(sns.boxplot, "$/sqft", orient='v')
#plt.show()

#bedrooms = plt.subplots()
#bathrooms = plt.subplots()
#ppsqft = plt.subplots()
#bedrooms = sns.distplot(tf.bedrooms,kde=True)
#bedrooms.set_title('number of bedrooms in apartments for rent on craigslist')
#plt.show()
#bathrooms = sns.distplot(tf.bathrooms,kde=False,rug=False)
#bathrooms.set_title('number of bathrooms in apartments for rent on craigslist')
#plt.show()
#ppsqft = sns.kdeplot(areaTable['$/sqft'],shade=True)
#ppsqft.set_title('distribution of price per square foot for recent apartments listed for rent on craigslist')
#plt.show()

# Remove outliers by price per square foot
#outliers = areaTable[areaTable['normalized_ppsqft']>3.5 or areaTable['normalized_ppsqft']<-3.5]
#print(outliers.describe())
#print("^^AREA TABLE OUTLIERS^^")
#tf = tf.drop(outliers.index)

# Remove outliers for number of bedrooms (>3.5 stdev +/-)
#outliers = univariateSlice[univariateSlice['normalized_bedrooms']>3.5 or univariateSlice['normalized_bedrooms']<-3.5]
#print(outliers.describe())
#print("^^BEDROOM OUTLIERS^^")
#tf = tf.drop(outliers.index)

# Remove outliers for number of bedrooms
#outliers = univariateSlice[univariateSlice['normalized_bathrooms']>3.5 or univariateSlice['normalized_bathrooms']<-3.5]
#print(outliers.describe())
#print("^^BATHROOM OUTLIERS^^")
#tf = tf.drop(outliers.index)

def remove_outliers(tf):
# Remove outliers by price (absolute)
	outliers = tf[tf['price']>20000]
	tf=tf.drop(outliers.index)
	outliers = tf[tf['price']<100]
	tf=tf.drop(outliers.index)

	ax=generateHeatmap(areaTable,['neighborhood','bedrooms','bathrooms','price','sqft','$/sqft','pets?'])
	ax.set_title("Pairwise correlation of descriptive statistics")
	plt.show()

	byNeighborhood = areaTable.groupby('neighborhood')
	junk = byNeighborhood.filter(lambda x : len(x)<20).index
	declutterArea = areaTable.drop(junk)

	byNeighborhood = tf.groupby('neighborhood')
	junk = byNeighborhood.filter(lambda x : len(x)<20).index
	declutterAll = tf.drop(junk)


def main():
	densityByNeighborhood(declutterAll,colName='price')
	densityByNeighborhood(declutterArea,colName='sqft')
	densityByNeighborhood(declutterArea,colName='$/sqft')

	sns.set(style="white")
	ax=sns.relplot(x="sqft", y="price", hue="pets?",size="bedrooms", sizes=(40,400), alpha=0.3, palette="muted", data=declutterArea)
	plt.show()

	print(tf.describe())

# Create a boolean column whether pets are allowed
#petsTable = tf.copy()
#petsTable['pets?'] = petsTable.apply(lambda x : PetsOK(x),axis=1)
#petLogicCheck = petsTable.loc[:,['attributes','pets?']]
#print(petLogicCheck[petsTable['pets?'] == False])
#print(petLogicCheck.describe())

#ax = sns.boxplot(x='pets?', y='price', data=petsTable, orient="v")
#plt.show()


#ax = sns.pairplot(tf[['neighborhood','bedrooms','bathrooms','price']], hue='neighborhood',size=2.5)
#plt.show()

#print(tf.describe())

#ax = sns.boxplot(x='price',data=tf,orient='v')
#plt.show()

	gl.saveDataFrame(tf,fileName=outputFile)
	if debugVis:
		tf.to_csv('debug_'+outputFile+'.csv')



if __name__ == '__main__':
	main()
