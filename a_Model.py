import pandas as pd
from pandas import DataFrame,Series
import pandas.io.sql 
import pymysql as mdb
import numpy as np
import random
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def getWineList(cosSim,cur):
	l=len(cosSim)
	topTen=np.argsort(np.transpose(cosSim))
	topTen=topTen[:,l-15:l]
	topTen=np.ravel(topTen)

	return topTen

def getReviews(ind,cur):
	reviews=pd.DataFrame()
	for i in ind:
		cur.execute("SELECT indx,review FROM snapCTreviews WHERE indx     ='%s';" %i)
		query_results = cur.fetchall()
		revs=pd.DataFrame(list(query_results))
		reviews=reviews.append(revs)
	return reviews

def getWines(ind,cur):
	recWineList=pd.DataFrame()
	for i in ind:
		cur.execute("SELECT indx,wineName, year, wineVariant,  ratingScore FROM snapCTwine WHERE indx     ='%s';" %i)
		query_results = cur.fetchall()
		existingWines=pd.DataFrame(list(query_results))
		recWineList=recWineList.append(existingWines)
	return recWineList


def getTopTenWine(vec,svd, allRevsSVD,**kwargs):
	# enter in the for of w='name', keywords='words', numWines=
	
	# see what arguemenst were passed and parse them into their respective variable or assign default values
	w = kwargs.get('w','')
	keyWords=kwargs.get('keyWords','')
	numWines=kwargs.get('numWines',9)
	recWineList=pd.DataFrame()

	db = mdb.connect(user="root", host="localhost", passwd="cortex", db="cellarTracker")
		
	with db: 
		cur = db.cursor()
		if len(w) > 1: # if a wine name was provided  look it up in the db #### need to implement partial string matches
				cur.execute("SELECT indx,wineName, year,wineVariant,  ratingScore FROM snapCTwine WHERE wineName     ='%s';" %w)
				query_results = cur.fetchall()
				if len(query_results) > 0: # if a wine was returned
					existingWines=pd.DataFrame(list(query_results))
					
					for ind in existingWines[0]: # get cosSim for each wine and extract most similar wines from 
						cosSim=cosine_similarity(allRevsSVD,allRevsSVD[ind,:])
						wineInd=getWineList(cosSim,cur)
						recWineList=recWineList.append(getWines(wineInd,cur))
				
				elif len(query_results) == 0: # if no wines are returned set to 0
					recWineList=0
						
		elif len(keyWords) >0:
			keyWords=keyWords.lower()
			keyWords=re.sub(r'[\W_]+', ' ', keyWords)
			keyWords=re.sub(r'[\d_]+', ' ', keyWords)
			keyWords=keyWords.split()
			keyWordsVec=vec.fit_transform(keyWords)
			keyWordsSVD=svd.transform(keyWordsVec)
			cosSim=cosine_similarity(allRevsSVD,keyWordsSVD)
			wineInd=getWineList(cosSim,cur)
			recWineList=recWineList.append(getWines(wineInd,cur))
		else: 
			recWineList=[]

		if len(recWineList) == 0: # suggest a random selection of wines - eventually this should be from the astor database
			rows=len(allRevsSVD)
			allIDX=range(rows)
			random.shuffle(allIDX)
			recWineList=recWineList.append(getWines(allIDX[:10],cur))
		
	recWineList=recWineList.sort(columns=3,ascending=False).drop_duplicates()
	recWineList=recWineList[recWineList[3] != ' 0']

	#access reviews for recommended wines
	ind=recWineList[0]
	review=getReviews(ind,cur)

	recWineList=pd.concat([recWineList,review],axis=1)
	recWineList.columns=range(7)
	recWineList=recWineList.reset_index()
	return recWineList[:10]







