import simplejson as json
import data
import os

def fixAttributesInFile():
	datafile = data.openJsonFile("Data/cocktail.txt")
	for entry in datafile:
		if not 'attributes' in entry:
			tempDict = {}
			yelpAttrs = data.getAttributesFromYelp(entry['name'])
			for key, value in yelpAttrs.items():
				tempDict[key] = value
			entry['attributes'] = tempDict
	data.saveJsonToFile(datafile, "Data/db_cocktail_fixed.json")

def checkHowManyWithoutAttributes(filename):
	places = data.openJsonFile(filename)
	count = 0
	for entry in places:
		if not 'attributes' in entry:
			count+=1
			print entry['name']
	print "Total:", count

def checkLessThanAttributes(filename, numOfAtt):
	places = data.openJsonFile(filename)
	count = 0 
	for entry in places:
		if (len(entry['attributes'].keys()) < numOfAtt):
			print entry['name']
			count += 1
	print "Total with less than", numOfAtt, "attributes:", count

def checkHowManyDuplicatesInFiles(baseFile, toAppendFile, save=False):
	list1 = data.openJsonFile(baseFile)
	list2 = data.openJsonFile(toAppendFile)
	found = False
	duplicates = set()
	foundDuplicates = 0
	for entry1 in list1:
		for entry2 in list2:
			if entry1['name'] == entry2['name']:
				found = True
				break
		if found:
			print "Removing", entry2['name'], "from list2"
			list2.remove(entry2)
			foundDuplicates+=1
			found = False
	print "Total duplicates:",foundDuplicates
	if save:
		#list1.extend(list2)
		data.saveJsonToFile(list2, "Data/extended_list.json")

# On save, saves a new file with file1_clean.json name, leaving the old one in tact
def checkHowManyDuplicates(file1, save=False):
	list1 = data.openJsonFile(file1)
	cleanList = []
	seen = set()
	duplicates = set()
	for i, entry in enumerate(list1):
		if entry['name'] in seen:
			print "Duplicate:",entry['name'], "at index==",i
			duplicates.add(i)
		else:
			seen.add(entry['name'])
			cleanList.append(entry)
	if not duplicates:
		print "No duplicates found"
	else:
		if save:
			head, tail = os.path.split(file1)
			tail = tail[:-5]
			filename = ''.join(["Data/", tail, "_clean.json"])
			data.saveJsonToFile(cleanList, filename)

def filterPlacesWithAttributes(filename,save=False):
	places = data.openJsonFile(filename)
	placesAttributes = []
	placesNoAttributes = []
	for entry in places:
		if 'attributes' in entry:
			placesAttributes.append(entry)
		else:
			placesNoAttributes.append(entry)
	if save:
		head, tail = os.path.split(filename)
		tail = tail[:-5]
		filename_bad = ''.join(["Data/toFix/hookah_", tail, "_bad.json"])
		data.saveJsonToFile(placesNoAttributes, filename_bad)
		appendListToDB(placesAttributes, "db");
	return placesAttributes, placesNoAttributes

def appendFileToDB(filename, dbName):
	try:
		mainDB = data.openJsonFile("Data/"+dbName+".json")
		toAppend = data.openJsonFile(filename)
		mainDB.extend(toAppend)
		data.replaceJsonInFile(mainDB, "Data/"+dbName+".json")
	except IOError:
		print "Database doesn't exist. Will create a new file"
		data.replaceJsonInFile(places, "Data/db_hookah.json")

def appendListToDB(places, dbName):
	try:
		mainDB = data.openJsonFile("Data/"+dbName+".json")
		mainDB.extend(places)
		data.replaceJsonInFile(mainDB, "Data/"+dbName+".json")
	except Exception as e:
		print "Database doesn't exist. Will create a new file"
		data.replaceJsonInFile(places, "Data/"+dbName+".json")

def listValuesOfAttribute(attribute, filename):
	places = data.openJsonFile(filename)
	valueList = set()
	attributeCounter = {}
	for place in places:
		if attribute in place['attributes']:
			if place['attributes'][attribute] not in valueList:
				valueList.add(place['attributes'][attribute])
	for entry in valueList:
		print entry
	return valueList

def countValuesOfAttributes(attribute, filename):
	places = data.openJsonFile(filename)
	valueList = listValuesOfAttribute(attribute, filename)
	yesCount = noCount = 0 
	for place in places:
		if attribute in place['attributes']:
			if place['attributes'][attribute] == "Yes":
				yesCount+=1
			else:
				noCount+=1
	print "Yesses:", yesCount
	print "Noess:", noCount

def deletePlacesWithAttribute(filename, attribute, value):
	places = data.openJsonFile(filename)
	new_list = places[:]
	att_count = 0
	for place in places:
		if attribute in place['attributes']:
			if place['attributes'][attribute] == value:
				new_list.remove(place)
				att_count +=1
	print att_count
	#data.saveJsonToFile(new_list, "Data/db.json")

def countAttributes(filename):
	datafile = data.openJsonFile(filename)
	attributes_set = set()
	for entry in datafile:
		for key,value in entry['attributes'].iteritems():
			attributes_set.add(key)

	attribute_counter = {}
	for att in attributes_set:
		attribute_counter[att] = 0

	for entry in datafile:
		for key,value in entry['attributes'].iteritems():
			if key in attributes_set:
				count = attribute_counter[key]
				attribute_counter[key] += 1

	for entry in sorted(attribute_counter, key=attribute_counter.get, reverse=True):
		print entry, attribute_counter[entry]

#checkHowManyDuplicates("Data/cleaned_cocktail.json")
#newPlaces = checkHowManyDuplicates("data/db_cocktail_copy.json", "data/place5_good.txt")
#data.saveJsonToFile(newPlaces, "data/noduplicates.txt")
#checkHowManyDuplicates("Data/db_cocktail_clean.json")

### ROUTINE ###
## PATH TO DB: 
## 		Cocktail: "Data/db_cocktail.json"
##		Hookah:   "Data/db_hookah.json"
#checkHowManyDuplicatesInFiles("Data/db_cocktail.json", "Data/toFix/place5_bad.json")
if __name__ == '__main__':
	checkLessThanAttributes("Data/hunterDB.json", 4)