from sklearn.externals import joblib
def loadModels():
	global vec,svd, allRevsSVD
	allRevsSVD=joblib.load('/insightProject/wineRecommender/allRevsSVD.pkl')
	vec=joblib.load('/insightProject/wineRecommender/tfidfVec.pkl')
	svd=joblib.load('/insightProject/wineRecommender/svd.pkl')
	return vec,svd, allRevsSVD
