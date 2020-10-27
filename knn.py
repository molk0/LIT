import db
import numpy as np
from sklearn.cluster import KMeans
from sklearn import metrics
from scipy.spatial import distance

MULTI_ATT_LIST = ('Accepts Credit Cards', 'Good for Groups', 'Has TV', 'Happy Hour',
	'Good For Dancing', 'Good for Kids', 'Alcohol', 'Smoking', 'Noise Level')

COLLECTION = 'locations'
DATAFILE = db.getLocations(COLLECTION)

def return_category_indexes():
	categories = set()
	index = 0
	categoryList = []
	for place in DATAFILE:
		if place['category'] not in categories:
			categories.add(place['category'])
			categoryList.append(place['category'])
			index+=1
	return categoryList

def attribute_initialization_place():
	total_list=[]
	categoryList = return_category_indexes()
	for place in DATAFILE:
	    place_list = []
	    for att in MULTI_ATT_LIST:
	        if att in place['attributes'].keys() and place['attributes'][att]=='Yes':
	            place_list.insert(MULTI_ATT_LIST.index(att), 1)
	        elif att == 'Alcohol' and att in place['attributes'].keys():
	        	if place['attributes'][att] == 'Full Bar' or place['attributes'][att] == 'Beer & Wine Only':
	        		place_list.insert(MULTI_ATT_LIST.index(att), 1)
	        	else:
	        		place_list.insert(MULTI_ATT_LIST.index(att), 0)
	        		# might wanna raise error if unknown value seen
	        elif att == 'Smoking' and att in place['attributes'].keys():
	        	if place['attributes'][att] == 'Yes' or place['attributes'][att] == 'Outdoor Area/ Patio Only':
	        		place_list.insert(MULTI_ATT_LIST.index(att), 1)
	        	else:
	        		place_list.insert(MULTI_ATT_LIST.index(att), 0)
	        		# might wanna raise error if unknown value seen
	        elif att == 'Noise Level' and att in place['attributes']:
	        	if place['attributes'][att] == 'Quiet':
	        		place_list.insert(MULTI_ATT_LIST.index(att), 1)
	        	elif place['attributes'][att] == 'Average':
	        		place_list.insert(MULTI_ATT_LIST.index(att), 2)
	        	elif place['attributes'][att] == 'Loud':
	        		place_list.insert(MULTI_ATT_LIST.index(att), 3)
	        	elif place['attributes'][att] == 'Very Loud':
	        		place_list.insert(MULTI_ATT_LIST.index(att), 4)
	        else:
	            place_list.insert(MULTI_ATT_LIST.index(att), 0) 
	    place_list[0] = categoryList.index(place['category'])
	    total_list.append(place_list)
	return total_list

def attribute_initialization_user(userInfo):
	user_list = []
	for att in MULTI_ATT_LIST:
		if userInfo[att] == 'Yes':
			user_list.insert(MULTI_ATT_LIST.index(att), 1)
		else:
			user_list.insert(MULTI_ATT_LIST.index(att), 0)
	return user_list

def get_numpy_attributes():
	numpy_matrix = np.zeros((len(DATAFILE)))
	total_list = attribute_initialization_place()
	numpy_matrix = np.array([np.array(x) for x in total_list])
	for i in range(len(DATAFILE)):
		multiplyWeights(numpy_matrix[i])
	return numpy_matrix

def get_user_from_db():
	try:
		user = db.retrieveUserAndConvert()
		return user
	except Exception as e:
		db.dealWithException(e)
		sys.exit("ml.py: Error while retrieving user from db. Execution halted.")

def return_user_numpy():
	user = get_user_from_db()
	userBinary = attribute_initialization_user(user)
	user_numpy = np.array(userBinary)
	multiplyWeights(user_numpy)
	return user_numpy

#Makes changes to avg_list
def get_cluster_min(avg_list):
	min_index = avg_list.index(min(avg_list))
	avg_list[min_index] = 100
	return min_index

def multiplyWeights(numpy_array):
	numpy_array[3]=(numpy_array[3]+1)*2
	numpy_array[4]=(numpy_array[4]+1)*3
	numpy_array[5]=(numpy_array[5]+1)*3
	numpy_array[6]=(numpy_array[6]+1)*5
	numpy_array[8]=(numpy_array[8]+1)*4

def get_results(top_1, top_2, top_3):
	result = []
	result_count = 1
	one,two,three = 0, 0, 0
	for i in range(30):
		if i % 4 == 0:
			try:
				result.append(top_3[three])
				three+=1
			except IndexError:
				pass
		elif i % 3 == 0:
			try:
				result.append(top_2[two])
				two+=1
			except IndexError:
				pass
		else:
			try:
				result.append(top_1[one])
				one+=1
			except IndexError:
				pass

def main():
	numpy_attributes = get_numpy_attributes()
	user_numpy = return_user_numpy()
	
	N_CLUSTERS = 40
	clusters = KMeans(n_clusters=N_CLUSTERS).fit(numpy_attributes)
	avg_cluster = [[] for i in range(N_CLUSTERS)]
	all_distances = []
	for index, cluster in enumerate(clusters.labels_):
		place_dist = distance.euclidean(user_numpy, numpy_attributes[index])
		avg_cluster[cluster].append(place_dist)
		all_distances.append(place_dist)

	avg_cluster = [np.mean(a) for a in avg_cluster]
	top_indexes = [get_cluster_min(avg_cluster) for i in range(3)]

	top_1, top_2, top_3 = ([] for i in range(3))
	zipped_clusters = sorted(zip(clusters.labels_, all_distances, DATAFILE))
	
	for index, i in enumerate(zipped_clusters):
		if i[0]==top_indexes[0]:
			i[2]['level'] = 1
			top_1.append(i[2])
		if i[0]==top_indexes[1]:
			i[2]['level'] = 2
			top_2.append(i[2])
		if i[0]==top_indexes[2]:
			i[2]['level'] = 3
			top_3.append(i[2])

	result_list = get_results(top_1, top_2, top_3)
	print len(result_list)
	for loc in result_list:
		print loc['name']

if __name__ == '__main__':
	# Add query to database for testing
	from add_query import add_query
	add_query("573e49306f97e3013cb8c3da", 40.768533, -73.965363)
	
	main()
	

