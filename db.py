from pymongo import MongoClient
from bson.objectid import ObjectId
import simplejson as json
import ssl
import time

start = time.clock()
def connect():
	client = MongoClient('mongodb://localhost:27017/')
	db = client.test
	return db

def addLocations(filename):
	db = connect()
	jsonObj = open(filename, "r")
	locList = json.load(jsonObj)
	for loc in locList:
		db.hunterLocs.insert(loc)
	print "Locations added"

def getLocations(collectionName):
	db = connect()
	datafile = db[collectionName].find()
	datafile_list = []
	for loc in datafile:
		datafile_list.append(loc)
	return datafile_list

def getLength(collectionName):
	db = connect()
	count = db[collectionName].count()
	return count

def getUserInfo(userId):
	db = connect()
	info = db.user.find_one({"_id": ObjectId(userId)})
	return info

def addUser():
	db = connect()
	exampleUser = {"_class" : "com.example.user", "userName" : "phil@smd", "password" : "yoyo0000", "Accepts_Credit_Cards" : 3.799999999999997, "Good_for_Groups" : 3.3999999999999986, "Has_TV" : 1.3500000000000003, "Happy_Hour" : 3.3499999999999988, "Good_For_Dancing" : 1, "Good_for_Kids" : 1.5000000000000004, "Alcohol" : 3.4499999999999984, "Smoking" : 1.3500000000000003, "Noise_Level" : { "Quiet" : 1, "Average" : 1, "Loud" : 3, "Very_Loud" : 1 } }
	db.user.insert_one(exampleUser)

def returnUserAttributesFormat(userInfo):
	newUserDict = {}
	discardAttributes = ("userName", "_id", "new_user", "password", "_class")
	try:
		for key,value in userInfo.iteritems():
			if key not in discardAttributes:
				if ("_") in key:
					key = key.replace("_", " ")
					try:
						newUserDict[key] = float(value)
					except TypeError:
						print "TypeError when assigning float on", key
						newUserDict[key] = value
				else:
					newUserDict[key] = value
			if key == "Noise Level":
				newUserDict[key] = returnNoiseValue(newUserDict[key])
	except AttributeError:
		pass
	return newUserDict

def returnNoiseValue(noiseAttributes):
	highestKeyValue = ""
	currentKeyValue = 0
	for key, value in noiseAttributes.iteritems():
		if value > currentKeyValue:
			highestKeyValue = key
			currentKeyValue = value
	return {
		"Quiet":1,
		"Average":2,
		"Loud":3,
		"Very_Loud":4
	}[highestKeyValue]

def normalizeUserValues(userInfo):
	valueMin = min(userInfo.itervalues())
	valueMax = max(userInfo.itervalues())
	for key, value in userInfo.iteritems():
		if key == "Noise Level":
			pass
		else:
			value = (value-valueMin)/(valueMax-valueMin)
			userInfo[key] = value

def formatFloatToBinary(userInfo):
	for key,value in userInfo.iteritems():
		if key == "Noise Level":
			pass
		else:
			if value>0.5:
				userInfo[key] = "Yes"
			else:
				userInfo[key] = "No"
def convert(userInfo):
	user = returnUserAttributesFormat(userInfo)
	normalizeUserValues(user)
	formatFloatToBinary(user)
	return user

def retrieveUserFromQuery():
	db = connect()
	user = db.query.find_one()
	return user

def removeUserFromQuery():
	db = connect()
	db.query.drop()

def retrieveUserFromUserDB():
	db = connect()
	userInfo = retrieveUserFromQuery()
	objectId = userInfo['id']
	user = db.user.find_one({"_id": ObjectId(objectId)})
	return user

def retrieveUserAndConvert():
	user = retrieveUserFromUserDB()
	user = convert(user)
	removeUserFromQuery()
	return user

def uploadResult(result_list):
	db = connect()
	checkIfAlreadyExists(db)
	for result in result_list:
		db.result.insert_one(result)

def checkIfAlreadyExists(db):
	collections = db.collection_names()
	if "result" in collections:
		print "ERROR: Collection \"result\" already exists. Deleting."
		db.result.drop()

def uploadErrorResult():
	result = {
		'error': 'Error while retrieving user from database',
		'error_code': '401',
		}
	result_list = [result]
	uploadResult(result_list)

def dealWithException(e):
	print e.__doc__
	print e.message
	print "Database error: Problem with the query."
	removeUserFromQuery()
	uploadErrorResult()
	
# end = time.clock()
# print "Execution time: ", (end-start)