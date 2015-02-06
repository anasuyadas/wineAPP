from flask import Flask
app=Flask(__name__)

from flask import render_template, request
from app import app
import pymysql as mdb

from a_Model import getTopTenWine
import pandas 
from pandas import DataFrame,Series
from sklearn.externals import joblib
import re
def populateDropDown():
	db = mdb.connect(user="root", host="localhost", passwd="cortex", db="cellarTracker")
	results = None
	with db:
		cur = db.cursor()
		cur.execute("SELECT indx,wineName FROM snapCTwine WHERE CRC32(indx) % 10 = 0 limit 100;")
		global results
		results = cur.fetchall()
	return results


def loadModels():
	global vec,svd, allRevsSVD
	allRevsSVD=joblib.load('app/pkls/allRevsSVDThou.pkl')
	vec=joblib.load('app/pkls/tfidfVec.pkl')
	svd=joblib.load('app/pkls/SVDThou.pkl')
	return vec,svd, allRevsSVD

results=populateDropDown()


@app.route('/')
@app.route('/index')	
@app.route('/input')
def wine_input():
	global results
	return render_template("input.html", results=results)

@app.route('/output')
def wine_output():
	#pull 'ID' from input field and store it
	searchTerm=[]
	
	try:
		wineDrop = request.args.get('wineDrop').encode()
		wineDrop=wineDrop[1:]
	except:
		wineDrop=[]

	
	try:
		wine = request.args.get('wine').encode()
	except:
		wine=[]

	try:
		keyWords=request.args.get('key').encode()
		searchTerm=KeyWords
	except:
		keyWords=[]
	# with db:
	# 	cur = db.cursor()
	# 	#just select the city from the world_innodb that the user inputs
	# 	cur.execute("SELECT wineName, year, wineVariant, ratingScore FROM snapCTwine WHERE Name='%s' limit 1;" % wine)
	# 	query_results = cur.fetchall()
	wines=[]
	global results


	status,recWines= getTopTenWine(w=wine,wDrop=wineDrop,keyWords=keyWords)
	#recWines.columns=['indx','row','wineName','year','grape','ratingScore','indx2','review']
	if status[0]==1:
		for w in recWines.index:
			row=recWines.ix[w]
			row[7]=re.sub('<.*?>',' ',row[7])
			row[4]=re.sub('"','',row[4])
			wines.append(dict(wineName=row[2], wineVariant=row[4], ratingScore=row[5],review=row[7], img=row[9],buyUrl=row[10]))
		return render_template("output.html", wines=wines,results=results, searchTerm=searchTerm,status=status)
		  #call a function from a_Model package. note we are only pulling one result in the query
	else: 
	#wines=recWines.to_json(orient='index')
		return render_template("output.html",results=results, status=status)


