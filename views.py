from flask import render_template, request
from app import app

from a_Model import getTopTenWine
import pandas 
from pandas import DataFrame,Series
from sklearn.externals import joblib

def loadModels():
	global vec,svd, allRevsSVD
	allRevsSVD=joblib.load('/insightProject/wineRecommender/allRevsSVD.pkl')
	vec=joblib.load('/insightProject/wineRecommender/tfidfVec.pkl')
	svd=joblib.load('/insightProject/wineRecommender/svd.pkl')
	return vec,svd, allRevsSVD

vec,svd, allRevsSVD=loadModels()

@app.route('/index')
def index():
	return render_template("input.html")
	
@app.route('/input')
def wine_input():
	return render_template("input.html")

@app.route('/output')
def wine_output():
	#pull 'ID' from input field and store it
	
	try:
		wine = request.args.get('wine').encode()
		wine=' '+wine
	except:
		wine=[]

	try:
		keyWords=request.args.get('key').encode()
	except:
		keyWords=[]
	# with db:
	# 	cur = db.cursor()
	# 	#just select the city from the world_innodb that the user inputs
	# 	cur.execute("SELECT wineName, year, wineVariant, ratingScore FROM snapCTwine WHERE Name='%s' limit 1;" % wine)
	# 	query_results = cur.fetchall()
	wines=[]
	global vec,svd, allRevsSVD
	recWines= getTopTenWine(vec,svd, allRevsSVD,w=wine,keyWords=keyWords)
	recWines.columns=['indx','row','wineName','year','grape','ratingScore','indx2','review']
	for w in recWines.index:
		row=recWines.ix[w]
		wines.append(dict(wineName=row[2], wineVariant=row[4], ratingScore=row[5],review=row[7]))
	  #call a function from a_Model package. note we are only pulling one result in the query
	#wines=recWines.to_json(orient='index')
	return render_template("output.html", wines=wines)

