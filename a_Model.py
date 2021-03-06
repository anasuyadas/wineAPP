import pandas as pd
from pandas import DataFrame,Series
import pandas.io.sql 
import pymysql as mdb
import numpy as np
import random
import re

from sklearn.externals import joblib

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

def getUrlImg(ind,cur):
	urlImg=pd.DataFrame()
	for i in ind:
		cur.execute("SELECT wineId, imageFile,url review FROM wineImageUrl WHERE wineId  ='%s';" %i)
		query_results = cur.fetchall()
		u=pd.DataFrame(list(query_results))
		urlImg=urlImg.append(u)
	return urlImg


def getWines(ind,cur):
	recWineList=pd.DataFrame()
	for i in ind:
		cur.execute("SELECT indx,wineId,wineName, year, wineVariant,  ratingScore FROM snapCTwine WHERE indx     ='%s';" %i)
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
			query="SELECT indx,wineName, year,wineVariant,  ratingScore FROM snapCTwine WHERE wineName LIKE "+"'%"+w + "%' LIMIT 10;"
			cur.execute(query)
			query_results = cur.fetchall()
			if len(query_results) > 0: # if a wine was returned
				existingWines=pd.DataFrame(list(query_results))
				
				for ind in existingWines[0]: # get cosSim for each wine and extract most similar wines from 
					cosSim=cosine_similarity(allRevsSVD,allRevsSVD[ind,:])
					wineInd=getWineList(cosSim,cur)
					recWineList=recWineList.append(getWines(wineInd,cur))
			
				msg='Ten wines were found similar to'+ w
				status=(1,msg)
			elif len(query_results) == 0: # if no wines are returned set to 0
				recWineList=0
				status=(0,'Sorry, unable to find any similar wines!!')		
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
			msg='Found ten wines with properties like'+ keyWords
			status=(1,msg)
	try:
		recWineList=recWineList.sort(columns=3,ascending=False).drop_duplicates()
		recWineList=recWineList[recWineList[3] != 0]
		ind=recWineList[0]
		review=getReviews(ind,cur)
		urlImg=getUrlImg(recWineList[1],cur)
		recWineList=pd.concat([recWineList,review,urlImg],axis=1)
		recWineList.columns=range(11)
		recWineList=recWineList.reset_index()
		return status,recWineList[:10]
	except: 
		status=(0,'Please enter at least one wine or keyword!!')
		return status,recWineList

	#access reviews for recommended wines
	



