#!/usr/bin/python3

import getLivedata as gl
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import os
import re

fileName = 'data.h5'
debugVis = 1

df = gl.getDataFromDisk(fileName)
os.system("cp "+fileName+" "+fileName+".bak")
#df = pd.read_csv("debug.csv")
#if debugVis:
#	df.to_csv('debug.csv')

#df = gl.getMissingInformation(df,limit=120)

#df2 = gl.purgeMissingData(df)


#
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', 16)

tf = df.copy()
print(tf.neighborhood.describe())
print(tf.neighborhood.value_counts())

def PetsOK(row):
	if bool(re.match(u'.*catsare.*',row.attributes)) or bool(re.match('.*dogsare.*',row.attributes)):
		return True
	else:
		return False

#tf['post_per_neighborhood'] = tf['neighborhood'].aggregate(np.count_nonzero)
#print(tf.tail())

# CLEAN UP OUTLIERS
#Drop records belonging to a neighborhood with fewer than 5 posts
byNeighborhood = tf.groupby('neighborhood')
junk = byNeighborhood.filter(lambda x : len(x)<5).index
tf=tf.drop(junk)

# Drop records with no bathrooms
junk=tf[tf['bathrooms']==0].index
tf=tf.drop(junk)

# Look for duplicate posts (same title + number of bedrooms)
print("Finding duplicates...\n")
junk=tf.loc[:,['pid','title','bedrooms']]
junk.sort_values(['pid'],ascending=True,inplace=True,axis=0)
print(junk[junk[['title','bedrooms']].duplicated(keep=False) == True].describe())
duplicates=tf.loc[junk[['title','bedrooms']].duplicated(keep='last') == True]
tf = tf.drop(duplicates.index)

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

areaData = tf[tf['sqft']>0]
areaTable = areaData.loc[:, ['neighborhood','bedrooms','bathrooms','sqft','attributes','price']]
areaTable['$/sqft'] = areaData.apply(lambda x : x.price/x.sqft,axis=1)
areaTable['pets?'] = areaData.apply(lambda x : PetsOK(x),axis=1)
print(areaTable.describe())
#ax = sns.boxplot(x='neighborhood', y='$/sqft', data=areaTable, orient="v")
#plt.show()
ax = sns.boxplot(x='pets?', y='$/sqft', data=areaTable, orient="v")
plt.show()

#ax = sns.distplot(tf.price)
#plt.show()

#fig,ax=plt.subplots()
#ax=sns.distplot(areaTable.sqft)
#ax.set_xlim(0,1000)
#ax.set_xticks(range(0,1000,100))
#plt.show()

#outliers = areaTable[areaTable['$/sqft']>7.5]
#print(outliers.describe())
#tf = tf.drop(outliers.index)

print(tf.describe())

# Create a boolean column whether pets are allowed
petsTable = tf.copy()
petsTable['pets?'] = petsTable.apply(lambda x : PetsOK(x),axis=1)
petLogicCheck = petsTable.loc[:,['attributes','pets?']]
#print(petLogicCheck[petsTable['pets?'] == False])
#print(petLogicCheck.describe())
ax = sns.boxplot(x='pets?', y='price', data=petsTable, orient="v")
plt.show()


#ax = sns.pairplot(tf[['neighborhood','bedrooms','bathrooms','price']], hue='neighborhood',size=2.5)
#plt.show()

#print(tf.describe())

gl.saveDataFrame(tf,fileName='cleandata.h5')
if debugVis:
	tf.to_csv('debug_cleandata.csv')


