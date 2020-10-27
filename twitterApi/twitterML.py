import simplejson as json
import calendar
import datetime
from sklearn.datasets import load_boston
import matplotlib.pyplot as plt
import numpy as np
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression

def analyzeTimeStamp(filename):
	listOfHours = []
	with open(filename, "r") as txtfile:
		for line in txtfile:
			if line.startswith('2'):
				timeline = line.split(" ")[1]
				listOfHours.append(timeline.split(":")[0])
				#print timeline.split(":")[0]
	return listOfHours

listOfHours = analyzeTimeStamp("localdb_test.txt")

hourCounter = {}
for hour in listOfHours:
	if hour in hourCounter:
 		hourCounter[hour]+=1
	else:
		hourCounter[hour] = 1

for key,value in hourCounter.iteritems():
	print key, ":", value

# def getDayOfWeek(filename):
# 	dateList = []
# 	with open(filename, "r") as txtfile:
# 		for line in txtfile:
# 			if line.startswith('2'):
# 				dateLine = line.split(" ")[0]
# 				#print date.split(" ")[0]
# 				dateSplit = dateLine.split("-")
# 				dateList.append(dateSplit)
# 	return dateList

class countHolder:
	def __init__(self, name, dayList):
		self.name = name
		self.dayList = dayList

	def printCounter(self):
		for indexDay, day in enumerate(self.dayList):
			for indexHour, hour in enumerate(day):
				if self.dayList[indexDay][indexHour] != 0:
					print "Currently", indexDay, "at", indexHour, "is equal to", self.dayList[indexDay][indexHour]

def formatLine(line):
	day = line.split(" ")[0]
	day = day.split("-")
	time = line.split(' ')[1]
	time = int(time.split(':')[0])
	day = datetime.date(int(day[0]), int(day[1]), int(day[2]))
	return datetime.datetime.weekday(day), time

# var1 = "2016-05-06 22:29:03"
# print formatLine(var1)

def initializeList():
	listvar = []
	for i in range(7):
		listvar.append([])
		for j in range(24):
			listvar[i].append(0)
	return listvar

def readFromFile(filename):
	placeName = ''
	dayList = initializeList()
	listOfPlaceObjects = []
	with open(filename, 'r') as txt:
		for line in txt:
			if line.startswith('%'):
				placeName = line.strip()
	 			placeName = placeName.replace('%', '')
	 		elif line.startswith('*****'):
	 			newPlace = countHolder(placeName, dayList)
	 			listOfPlaceObjects.append(newPlace)
	 			dayList = initializeList()
	 		else:
	 			#dayList[0][0] = 0 first 0 represents day of the week, second 0 represents hour and what it equals to is the counter
	 			day, hour = formatLine(line)
	 			dayList[day][hour] += 1
	return listOfPlaceObjects

totalList = []

listOfObjects = readFromFile("localdb_test.txt")
for objectt in listOfObjects:
	print objectt.name
	if objectt.name == "theponybarues":
		pony = objectt
	objectt.printCounter()
	totalList.append(np.array(objectt.dayList))

ponyY = [] # tweet count
ponyX = [i for i in range(168)] # number of hours in a week

# for x in pony.dayList:
# 	for y in x:
# 		ponyCount.append(pony.dayList[x][y])

for indexDay, day in enumerate(pony.dayList):
	for indexHour, hour in enumerate(day):
		tempList = []
		tempList.append(pony.dayList[indexDay][indexHour])
		ponyY.append(tempList)
		#ponyY.append(pony.dayList[indexDay][indexHour])

ponyYnp = np.array(ponyY)
ponyXnp = np.array(ponyX)
ponyXnp = ponyXnp.reshape(168, 1)
ponyYnp = ponyYnp.ravel()

model = LogisticRegression()
model.fit(ponyXnp, ponyYnp)
model.score(ponyXnp, ponyYnp)
print('Coefficient: \n', model.coef_)
print('Intercept: \n', model.intercept_)
predicted= model.predict_proba(167)
print predicted
# model = GaussianNB()
# model.fit(ponyXnp, ponyYnp)
# predicted= model.predict_proba(167)
# print predicted

# totalNumpy = np.array(totalList)
# print totalNumpy

# lista = initializeList()
# for entry in lista:
# 	print len(entry)



# def readFromFile(filename):
# 	placeName = ''
# 	tweetList = []
# 	locList = []
# 	with open(filename, 'r') as txt:
# 		for line in txt:
# 			if line.startswith('%'):
# 				placeName = line.strip()
# 				placeName = placeName.replace('%', '')
# 				placeDict = {}
# 				placeDict['name'] = placeName
# 			elif line.startswith('*****'):
# 				locList.append(placeDict)
# 			else:
# 				if 'tweets' in placeDict:
# 					placeDict['tweets'].append(line.strip())
# 				else:
# 					placeDict['tweets']=[line.strip()]		
# 	return locList

# placeDict = readFromFile('localdb_test.txt')
# for entry in placeDict:
# 	print entry

# dayList = getDayOfWeek("localdb_test.txt")

# dayOfWeek = []
# for day in dayList:
# 	print day
# 	d = datetime.date(int(day[0]), int(day[1]), int(day[2]))
# 	print datetime.datetime.weekday(d) #prints day of the week. 0 is monday. 6 is sunday.

# locations = [()]
# print locations


#for loop to navigate through text file
#read each line and record the hour when the tweet was posted
#counter for each hour
#dictionary to count the time stamps
#weather