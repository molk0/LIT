from pymongo import MongoClient
from bson.objectid import ObjectId
import db

def add_query(query_id, query_lat, query_lng):
	database = db.connect()
	query = {"id" : query_id, "lat" : query_lat, "lng" : query_lng}
	database.query.insert_one(query)
	print "Query added"

if __name__ == '__main__':
	add_query("5736c2d16f97e3161487f9a7", 40.768533, -73.965363)
