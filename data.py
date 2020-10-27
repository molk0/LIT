import urllib2
import sys
import foursquare
import simplejson as json
import unicodedata
import time
# import fix
from pymongo import MongoClient
from bs4 import BeautifulSoup

import settings
reload(sys)
sys.setdefaultencoding('utf-8')

fsClient = foursquare.Foursquare(client_id=settings.client_id, 
	client_secret=settings.client_secret)
attributesToDelete = ("hasMenu", "verified", "referralId", "venueChains", "menu", "storeId", 
	"hereNow", "specials", "allowMenuUrlEdit", "venuePage", "delivery")
REQUESTNUMBER = 0

def incrementAndPrintREQUESTNUMBER():
	global REQUESTNUMBER
	REQUESTNUMBER += 1
	if REQUESTNUMBER % 50 == 0:
		print "Request #", REQUESTNUMBER

def collectPlacesCont(ll, categoryId, finishedl):
	longitudeFloat = getFloatLongitude(ll)
	latitudeFloat = getFloatLatitude(ll)
	result = []
	while longitudeFloat < finishedl:
		result = deleteDuplicates(result)
		result.extend(collectPlaces(ll, categoryId))
		ll = addToCoordinate(ll)
		longitudeFloat = longitudeFloat + 0.004
	result = deleteDuplicates(result)
	assignAttributes(result)
	return result

def getFloatLongitude(ll):
	ll_split = ll.split(',')
	longitFloat = float(ll_split[1])
	return longitFloat

def getFloatLatitude(ll):
	ll_split = ll.split(',')
	latFloat = float(ll_split[0])
	return latFloat

def addToCoordinate(ll):
	ll_split = ll.split(',')
	longitFloat = float(ll_split[1])
	longitFloat = longitFloat + 0.006
	longitString = str(longitFloat)
	ll = ''.join([ll_split[0],',',longitString])
	return ll

# REMEMBER TO CHANGE CATEGORY FOR LOCATION CLEANUP
def collectPlaces(ll, categoryId, radius='200'):
	places = fsClient.venues.search(params={'ll': ll, 'radius': radius, 'categoryId':categoryId, 'limit':'50'})
	places = places['venues']
	incrementAndPrintREQUESTNUMBER()
	if len(places) == 50:
		print "ERROR: More than 50 places!"
		print "Error location: "; print ll
		print categoryId
	categoryName = getCategoryName(nightlifeCategory, categoryId)
	cleanLocations(places, categoryName)
	reformatCategory(places)
	return places

def collectPlacesWithAttributes(ll, categoryId, radius='200'):
	places = fsClient.venues.search(params={'ll': ll, 'radius': radius, 'categoryId':categoryId, 'limit':'50'})
	places = places['venues']
	if len(places) == 50:
		print "ERROR: More than 50 places!"
		print "Error location: "; print ll
		print categoryId
	categoryName = getCategoryName(recreationCategory, categoryId)
	cleanLocations(places, categoryName)
	reformatCategory(places)
	assignAttributes(places)
	return places

def cleanLocations(listOfLocs, category):
	listOfLocs[:] = [loc for loc in listOfLocs if loc['stats']['checkinsCount'] > 50 ]
	listOfLocs[:] = [loc for loc in listOfLocs if loc['categories'][0]['name'] == category]
	for loc in listOfLocs:
		for attr in attributesToDelete:
			if attr in loc:
				loc.pop(attr)

def deleteDuplicates(listToProcess):
	seen = set()
	result = []
	duplicates = 0
	for d in listToProcess:
		if d:
			h = d.copy()
			h.pop('id')
			h.pop('category')
			h.pop('contact')
			h.pop('location')
			h.pop('stats')		
			try:
				h.pop('attributes')
			except:
				pass
			try:
				h.pop('url')
			except:
				pass
			h = tuple(h.items())
			try:
				if h not in seen:
					result.append(d)
					seen.add(h)
				else:
					duplicates+=1
			except TypeError:
				print "Problem with", h[0]
	#print "Duplicates found: ", duplicates
	return result

def getCategoryName(catTuple, categoryId):
	for index, item in enumerate(catTuple):
		if item[1] == categoryId:
			return item[0]

def reformatCategory(listOfLocs):
	for loc in listOfLocs:
		category = loc['categories'][0]['name']
		loc['category'] = category
		loc.pop('categories')

def assignAttributes(listOfLocs, noyelp=None):
	for loc in listOfLocs:
		tempDict = {}
		# if (type(loc['name']) == unicode):
		# 	message = ''.join("UNICODE:"+loc['name'])
		# 	placesWithoutYelp.add(message)
		# 	pass
		yelpAttrs = getAttributesFromYelp(loc['name'])
		if(yelpAttrs):
			for key, value in yelpAttrs.items():
				tempDict[key] = value
			loc['attributes'] = tempDict

def getAttributesFromYelp(nameOfPlace):
	attributes = {}
	link = yelpify(nameOfPlace)
	soupObj = connectToYelp(link)
	try:
		short_def_list = soupObj.find("div", {"class": "short-def-list"})
		for dl in short_def_list.findAll("dl"):
			attributes[dl.dt.getText().strip()] = dl.dd.getText().strip()
	except AttributeError: 
		print "Error: Page doesn't exist for",
		print nameOfPlace
		#placesWithoutYelp.add(nameOfPlace)
	return attributes

def getAttributesFromLink(link):
	attributes = {}
	link = link
	soupObj = connectToYelp(link)
	short_def_list = soupObj.find("div", {"class": "short-def-list"})
	for dl in short_def_list.findAll("dl"):
		attributes[dl.dt.getText().strip()] = dl.dd.getText().strip()
	return attributes

def yelpify(place):
	place = urlify(place)
	yelpBase = "https://www.yelp.com/biz/"+place+"-new-york"
	return yelpBase

def urlify(place):
	if ('&' in place):
		place = place.replace("&", "and")
	if ("'" in place):
		place = place.replace("'", "")
	return "-".join(place.split())

def connectToYelp(link):
	try:
		page = urllib2.urlopen(link)
		soup = BeautifulSoup(page.read())
		return soup
	except urllib2.HTTPError:
		pass
	except UnicodeEncodeError:
		print "ERROR: Unicode error"

def savePlacesWithoutYelp():
	with open('Data/placesWithoutYelp.txt', 'a') as outfile:
		for item in placesWithoutYelp:
			outfile.write(item+"\n")
	
def readCategoryFile(filename):
	catList = []
	with open(filename, 'r') as outfile:
		for line in outfile.readlines():
			tmp = line.split(',')
			name = tmp[0].strip()
			catId = tmp[1].strip()
			result = (name, catId)
			catList.append(result)
	catTuple = tuple(catList)
	return catTuple
 
def replaceJsonInFile(listToSave, filename):
	with open(filename, 'w') as outfile:
 		json.dump(listToSave, outfile)	

def saveJsonToFile(listToSave, filename):
	with open(filename, 'a') as outfile:
		json.dump(listToSave, outfile)

def openJsonFile(filename):
	jsonObj = open(filename, "r")
	parsedJson = json.load(jsonObj)
	return parsedJson

def readCoordinatesFromFile(filename):
	coordinateList = []
	with open(filename, 'r') as txt:
		for line in txt:
			line = line.strip()
			if not line.startswith("#"):
				coordTuple = tuple(line.split(','))
				coordinateList.append(coordTuple)
	return coordinateList


# CATEGORY VARIABLES
nightlifeCategory = readCategoryFile('D:/LIT/Data/Category/nightlife.txt')
artCategory = readCategoryFile('D:/LIT/Data/Category/arts.txt')
eventCategory = readCategoryFile('D:/LIT/Data/Category/events.txt')
recreationCategory = readCategoryFile('D:/LIT/Data/Category/recreation.txt')

def connectFiles():
	allPlaces = []
	# for category in nightlifeCategory:
	# 	categoryName = category[0]
	# 	filename = ''.join(["Data/allplaces_", categoryName, "_fixed.json"])
	# 	allPlaces.extend(openJsonFile(filename))
	for category in recreationCategory:
		categoryName = category[0]
	 	filename = ''.join(["Data/allplaces_", categoryName, "_fixed.json"])
	 	allPlaces.extend(openJsonFile(filename))
	saveJsonToFile(allPlaces, "Data/hunterDatabase_recreation.json")

def main():
	allPlaces = []
	coordinateList = readCoordinatesFromFile('Data/Coordinates/14th.txt')
	for category in nightlifeCategory:
		for coordinate in coordinateList:
			start = ''.join([coordinate[0], ',', coordinate[1]])
		 	end = float(coordinate[2])
		 	allPlaces.extend(collectPlacesCont(start, category[1], end))
	saveJsonToFile(allPlaces, 'Data/14/Nightlife.json')

if __name__ == '__main__':
	main()