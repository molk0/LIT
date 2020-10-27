import urllib2
import simplejson as json
import six
from instagram.client import InstagramAPI

client_id = 'client-id'
client_secret = 'client-secret'
access_token = 'access-token'
api = InstagramAPI(access_token=access_token)


def getUserID(username):
	response = urllib2.urlopen(
		"https://api.instagram.com/v1/users/search?q="
		+username+"&access_token="+access_token)
	json_id = json.load(response)
	_id = json_id['data'][0]['id']
	return _id

def getLocationsByCoordinates(lat, long):
	try:
		location_search = api.location_search(lat=lat, long=long, foursquare_id = "")
	except Exception as e:
		print(e)

def getRecentMediaByLocation(countOfPosts, locationID):
	url = "https://api.instagram.com/v1/locations/{location-id}/media/recent?access_token=ACCESS-TOKEN"
	websterhall, nextpage = api.location_recent_media(count=countOfPosts, 
		location_id=locationID)
	print websterhall

def displayBrandonInfo():
	brandon_id = get_user_id("br4ndonlu")
	print "Branon's ID:",
	print brandon_id

	count = 10
	rep_count = 0
	brandon_media, next_ = api.user_recent_media(user_id=brandon_id, count=count)

	for media in brandon_media:
		caption = str(media.caption)
		if "x3" in caption:
			result = caption.split()
			i=0
			for n in result:
				string = result[i]
				i+=1
				if "x3" in string:
					print "Brenda did 3 reps, proof:",
					print string
					rep_count+=3